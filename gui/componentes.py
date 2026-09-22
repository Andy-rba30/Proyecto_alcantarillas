# -*- coding: utf-8 -*-
"""
gui/componentes.py
==================
Los componentes de interfaz que `legacy/Tc.py` ya tenia resueltos, en un solo
sitio para que los usen las DOS ventanas.

Por que existe este archivo
---------------------------
`CLAUDE.md` obliga a reutilizar el patron de `legacy/Tc.py` -- MarcoScroll,
Tooltip, campo validable -- y a no reinventar los componentes. Hasta aqui
`Tooltip` y `MarcoScroll` vivian dentro de `gui/app.py`, que es la ventana
principal. La ventana emergente de la Sec. 4.2/4.3 los necesita, y una ventana
emergente que importara de la principal crearia un ciclo (`app` -> `ventana` ->
`app`). Las dos alternativas eran copiarlos --- que es exactamente reinventar
--- o sacarlos a un modulo comun. Esto es lo segundo: MISMO CODIGO, movido.

`CampoValidable` es lo unico nuevo, y no es invento: es el `_campo_validable`
de `legacy/Tc.py` (etiqueta + Entry dentro de un Frame cuyo fondo se pinta de
rojo) con UNA diferencia deliberada, que la Sec. 4.3 exige: alli el borde se
pinta al pulsar «Calcular», y aqui SE PINTA AL ESCRIBIR. «Valida al escribir,
no al calcular» es una frase del plan, y la traduccion literal de esa frase es
un `trace_add` sobre la variable.

`BotonAccion` es lo segundo nuevo, y tampoco es invento: es el `tk.Button` que
las dos ventanas ya construian a mano --- mismo `relief="flat"`, mismo
`cursor="hand2"`, mismo par fondo/blanco --- con lo unico que ninguna de las
dos hacia: que al APAGARSE siga leyendose y diga por que. Un boton apagado es
un bloqueo, y en este proyecto un bloqueo se declara.
"""

from __future__ import annotations

import ast
import re
import sys
import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------------------
# El tema «Blueprint Slate»: paleta, tipografia y estilos con nombre
# ---------------------------------------------------------------------------
# UN SOLO SITIO para como se ve la interfaz. Hasta el rediseño visual cada
# ventana escribia sus propias tuplas de fuente («Segoe UI», 9) y sus propios
# hexadecimales, y la ventana principal, la emergente, los editores y la
# ayuda de entrada divergian en cuerpo de letra y en color. Lo que sigue es
# la paleta con nombre, la tipografia resuelta contra las fuentes instaladas
# y `aplicar_tema`, que configura los estilos ttk CON NOMBRE que las cuatro
# pestañas y las ventanas emergentes usan. Ningun color ni tamaño se decide
# fuera de aqui; quien construye un widget pide el estilo por su nombre.
#
# La paleta es la del estilo de referencia («Blueprint Slate»): fondo de la
# ventana, superficies de los paneles, un azul de accion, y tres colores de
# estado --- verde, ambar, rojo --- cada uno con su fondo suave para las
# insignias. NINGUN ESTADO SE COMUNICA SOLO POR COLOR: toda insignia y toda
# fila coloreada llevan el texto del estado al lado, porque el color es la
# segunda señal y no la primera.
FONDO = "#EEF0F3"          # fondo de la ventana y de las zonas entre paneles
SUPERFICIE = "#F8F9FB"     # superficie de los paneles, tablas y campos
LINEA = "#D7DCE3"          # lineas finas: bordes de campo, separadores
TEXTO = "#1E2730"          # texto principal
TEXTO_SUAVE = "#5C6773"    # texto secundario: ayudas, subtitulos, cabeceras
AZUL = "#2F6FB0"           # accion principal y foco
AZUL_OSCURO = "#245A90"    # el azul al pulsar
VERDE = "#157A4B"          # cumple / resuelto / cerrado
AMBAR = "#A96A10"          # aviso / declarado en caliente / diferido
ROJO = "#B23A2C"           # no cumple / pendiente / error
AZUL_SUAVE = "#E4EDF7"     # fondo de la fila seleccionada y de la insignia «info»
VERDE_SUAVE = "#E2F1E9"
AMBAR_SUAVE = "#FAEFDB"
ROJO_SUAVE = "#F8E4E1"
GRIS_SUAVE = "#E6E9EE"     # insignia neutra: «sin corrida», «-»
PISADO_SUAVE = "#F5E3C8"   # el pisado en caliente, distinto del declarado
BLANCO = "#FFFFFF"         # el campo donde se teclea

# Los tres nombres con que el resto de la interfaz pide los colores de
# estado. Se conservan porque los llamadores (`gui/editores.py`,
# `gui/ventana_normativa.py`, `gui/ayuda_entrada.py`) los leen por este
# nombre; lo que cambio es el valor, que ahora sale de la paleta de arriba.
COLOR_ERROR = ROJO
COLOR_AVISO = AMBAR
COLOR_OK = VERDE

# El azul del icono de ayuda «i». Es el mismo tono del boton de EJECUTAR de la
# ventana principal: un icono de ayuda no compite con la accion, la acompaña.
COLOR_AYUDA_FONDO = AZUL
COLOR_AYUDA_ACTIVO = AZUL_OSCURO

# El par del boton DESHABILITADO. No es estetica: es que un boton apagado
# tiene que poder LEERSE, porque su texto es lo unico que dice que haria si
# estuviera encendido.
#
# `tk.Button` no cambia su fondo al deshabilitarse --- solo pinta el texto con
# `disabledforeground`, que por defecto es `#a3a3a3` ---, de modo que el texto
# apagado queda sobre el MISMO color vivo del boton encendido. Medido sobre la
# ventana real, con los cinco fondos que este proyecto usa, el contraste que
# salia era de 1.30:1 a 2.33:1 (el peor, `#a3a3a3` sobre el verde de los
# botones de exportacion). El minimo legible es 4.5:1. Con este par sale
# 6.93:1, y el fondo apagado ademas se DISTINGUE del encendido, que es la otra
# mitad de la señal.
COLOR_BOTON_APAGADO_FONDO = "#dfe3e6"
COLOR_BOTON_APAGADO_TEXTO = "#3d4b59"

# LA TIPOGRAFIA. Tres cuerpos de letra, nombrados --- y no escritos dentro de
# cada llamada --- porque son la decision de la interfaz entera y la tupla
# que los lleva se construye en `Tipografia`, no dentro de un widget. El
# barrido de literales de la capa de presentacion exime el entero que es
# argumento DIRECTO de una llamada de widget, y estos no lo son: van
# marcados, y `tests/test_sin_literales.py` los censa.
CUERPO_PT = 10     # literal-ok: cuerpo de letra de la interfaz, pt
PEQUENA_PT = 9     # literal-ok: letra pequeña (ayudas, rotulos de panel, insignias), pt
TITULO_PT = 14     # literal-ok: titulo de cada vista, pt

# Las familias, en orden de preferencia: IBM Plex si esta instalada, si no la
# del sistema (Segoe UI / Consolas en Windows, DejaVu en Linux). La
# monoespaciada es para numeros y claves; la de interfaz para todo lo demas.
FAMILIAS_UI = ("IBM Plex Sans", "Segoe UI", "Noto Sans", "DejaVu Sans",
               "Helvetica")
FAMILIAS_MONO = ("IBM Plex Mono", "Consolas", "Cascadia Mono",
                 "DejaVu Sans Mono", "Menlo", "Courier New")


# ---------------------------------------------------------------------------
# Nitidez en Windows: la conciencia de DPI se declara ANTES del primer Tk
# ---------------------------------------------------------------------------
# Medido sobre la ventana real en Windows tras el bloque 1: el titulo de la
# ventana (que pinta Windows) salia nitido y TODO el contenido (que pinta Tk)
# salia borroso. Es la firma de un proceso que no se declara consciente de
# DPI: con la pantalla al 125 % o al 150 %, Windows lo dibuja al 100 % y lo
# estira como una imagen. ttkbootstrap declara la conciencia «del sistema»
# al crear su `Window`, y no basta: vale solo para el monitor principal tal
# como estaba al iniciar sesion, y en cuanto la ventana cae en un monitor
# con otro escalado --- o el escalado cambio despues --- Windows vuelve a
# estirarla. La declaracion que no se estira nunca es la POR MONITOR (v2),
# y hay que hacerla antes de crear el primer `Tk`: despues, Windows la
# ignora. `gui.app.main` la llama en su primera linea.
#
# El valor es el pseudo-handle DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 de
# la API de Windows, no un valor de proyecto.
CONTEXTO_DPI_POR_MONITOR_V2 = -4   # literal-ok: pseudo-handle de la API de Windows
DPI_NO_APLICA = "no aplica: no es Windows"
DPI_POR_MONITOR_V2 = "por monitor (v2)"
DPI_POR_MONITOR = "por monitor"
DPI_DEL_SISTEMA = "del sistema"
DPI_NO_DECLARADA = "no se pudo declarar"


def declarar_conciencia_de_dpi():
    """
    Declara al proceso consciente de DPI en Windows, de la forma mas fina
    que el sistema admita, y devuelve cual quedo declarada (una de las
    cinco constantes `DPI_*`). Fuera de Windows no hace nada. Nunca lanza:
    una maquina sin la API moderna cae a la siguiente forma, y una sin
    ninguna se queda como estaba, que es lo que habia.
    """
    if sys.platform != "win32":
        return DPI_NO_APLICA
    import ctypes
    try:
        user32 = ctypes.windll.user32
        user32.SetProcessDpiAwarenessContext.argtypes = [ctypes.c_void_p]
        if user32.SetProcessDpiAwarenessContext(
                ctypes.c_void_p(CONTEXTO_DPI_POR_MONITOR_V2)):
            return DPI_POR_MONITOR_V2
    except (AttributeError, OSError):
        pass
    try:
        # 2 = PROCESS_PER_MONITOR_DPI_AWARE (Windows 8.1+).
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return DPI_POR_MONITOR
    except (AttributeError, OSError):
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        return DPI_DEL_SISTEMA
    except (AttributeError, OSError):
        return DPI_NO_DECLARADA


class Tipografia:
    """
    Las dos familias resueltas y los constructores de tuplas de fuente.

    `ui(tamano, *peso)` y `mono(tamano, *peso)` devuelven la tupla que Tk
    espera (`(familia, tamano, "bold")`). Se pide por nombre de cuerpo
    (`CUERPO_PT`, `PEQUENA_PT`, `TITULO_PT`), nunca con un numero suelto.
    """

    def __init__(self, ui_familia, mono_familia):
        self.ui_familia = ui_familia
        self.mono_familia = mono_familia

    def ui(self, tamano=CUERPO_PT, *peso):
        return (self.ui_familia, tamano, *peso)

    def mono(self, tamano=CUERPO_PT, *peso):
        return (self.mono_familia, tamano, *peso)


# La tipografia ACTIVA. Nace con las familias de Windows --- las que la
# interfaz usaba hasta el rediseño --- y `aplicar_tema` la resuelve contra
# las fuentes instaladas en cuanto hay un `Tk` con el que preguntar.
_TIPOGRAFIA = Tipografia(FAMILIAS_UI[1], FAMILIAS_MONO[1])


def tipografia():
    """La tipografia activa: la resuelta por `aplicar_tema`, o la de arranque."""
    return _TIPOGRAFIA


def _primera_instalada(preferidas, instaladas):
    for familia in preferidas:
        if familia in instaladas:
            return familia
    return preferidas[-1]


def resolver_tipografia(root):
    """
    Elige la primera familia instalada de cada lista y la deja activa.

    Pregunta a Tk (`tkinter.font.families`), que es lo unico que sabe que
    fuentes hay en ESTA maquina; sin `Tk` no hay a quien preguntar y se
    conserva la de arranque.
    """
    global _TIPOGRAFIA
    try:
        from tkinter import font as tkfont
        instaladas = set(tkfont.families(root))
    except (tk.TclError, ImportError, AttributeError):
        return _TIPOGRAFIA
    _TIPOGRAFIA = Tipografia(_primera_instalada(FAMILIAS_UI, instaladas),
                             _primera_instalada(FAMILIAS_MONO, instaladas))
    return _TIPOGRAFIA


# Las insignias de estado. Cada estado es un par (fondo suave, texto), y el
# estilo ttk de cada una se llama `<estado>.Insignia.TLabel`. Los cinco
# estados son los de la INTERFAZ (como se pinta una cosa), no los del
# calculo: el texto de la insignia es el que dice «cumple», «PENDIENTE»,
# «no cerrado»... y sale siempre del programa.
INSIGNIA_OK = "ok"
INSIGNIA_AVISO = "aviso"
INSIGNIA_ERROR = "error"
INSIGNIA_INFO = "info"
INSIGNIA_NEUTRA = "neutra"
INSIGNIAS = {
    INSIGNIA_OK: (VERDE_SUAVE, VERDE),
    INSIGNIA_AVISO: (AMBAR_SUAVE, AMBAR),
    INSIGNIA_ERROR: (ROJO_SUAVE, ROJO),
    INSIGNIA_INFO: (AZUL_SUAVE, AZUL),
    INSIGNIA_NEUTRA: (GRIS_SUAVE, TEXTO_SUAVE),
}


def estilo_de_insignia(estado):
    if estado not in INSIGNIAS:
        raise ValueError(f"insignia sin estado conocido: {estado!r}")
    return f"{estado}.Insignia.TLabel"


def aplicar_tema(style, root=None):
    """
    Configura los estilos ttk CON NOMBRE del tema, sobre el `Style` que la
    ventana ya tiene (el de ttkbootstrap si cargo, el de ttk si no).

    Los nombres que el resto de la interfaz pide:

    - marcos: `TFrame` (superficie), `Fondo.TFrame`, `Panel.TFrame`;
    - textos: `TLabel` (cuerpo, sobre superficie), `Fondo.TLabel`,
      `Paso.TLabel` («PASO n / 4»), `Titulo.TLabel`, `Subtitulo.TLabel`,
      `TituloPanel.TLabel` (mayusculas pequeñas), `Header.TLabel`,
      `Ayuda.TLabel`, `Error.TLabel`, `Res.TLabel` (monoespaciada en
      negrita), `Mono.TLabel`, `Estado.TLabel` (la barra de estado),
      `Proyecto.TLabel` (el nombre del proyecto en la barra superior);
    - insignias: `<estado>.Insignia.TLabel`, por `estilo_de_insignia`;
    - tablas: `Treeview` y `Treeview.Heading`, planas y densas;
    - el resto (`TEntry`, `TCombobox`, `TButton`, `TNotebook`,
      `TScrollbar`, `TPanedwindow`, `TSeparator`, `TRadiobutton`) toma la
      paleta sin cambiar de nombre.

    Se llama UNA vez, antes de construir widgets, porque `BotonAccion` y los
    `tk.Text` leen la tipografia resuelta al construirse.
    """
    tipo = resolver_tipografia(root) if root is not None else tipografia()
    ui, mono = tipo.ui, tipo.mono
    if root is not None:
        root.configure(background=FONDO)

    style.configure(".", background=SUPERFICIE, foreground=TEXTO, font=ui(),
                    bordercolor=LINEA, lightcolor=SUPERFICIE, darkcolor=LINEA,
                    troughcolor=FONDO, focuscolor=AZUL,
                    selectbackground=AZUL_SUAVE, selectforeground=TEXTO)
    style.configure("TFrame", background=SUPERFICIE)
    style.configure("Fondo.TFrame", background=FONDO)
    style.configure("Panel.TFrame", background=SUPERFICIE)

    style.configure("TLabel", background=SUPERFICIE, foreground=TEXTO, font=ui())
    style.configure("Fondo.TLabel", background=FONDO)
    style.configure("Paso.TLabel", background=FONDO, foreground=AZUL,
                    font=ui(PEQUENA_PT, "bold"))
    style.configure("Titulo.TLabel", background=FONDO, foreground=TEXTO,
                    font=ui(TITULO_PT, "bold"))
    style.configure("Subtitulo.TLabel", background=FONDO, foreground=TEXTO_SUAVE,
                    font=ui())
    style.configure("TituloPanel.TLabel", background=SUPERFICIE,
                    foreground=TEXTO_SUAVE, font=ui(PEQUENA_PT, "bold"))
    style.configure("Header.TLabel", font=ui(CUERPO_PT, "bold"), foreground=TEXTO)
    style.configure("Ayuda.TLabel", font=ui(PEQUENA_PT), foreground=TEXTO_SUAVE)
    style.configure("Error.TLabel", font=ui(PEQUENA_PT, "bold"), foreground=ROJO)
    style.configure("Res.TLabel", font=mono(CUERPO_PT, "bold"), foreground=TEXTO)
    style.configure("Mono.TLabel", font=mono())
    style.configure("Estado.TLabel", background=FONDO, foreground=TEXTO_SUAVE,
                    font=ui(PEQUENA_PT))
    style.configure("Proyecto.TLabel", background=FONDO, foreground=TEXTO,
                    font=ui(CUERPO_PT, "bold"))
    for estado, (fondo, frente) in INSIGNIAS.items():
        style.configure(estilo_de_insignia(estado), background=fondo,
                        foreground=frente, font=mono(PEQUENA_PT, "bold"),
                        padding=(7, 2))

    style.configure("TEntry", fieldbackground=BLANCO, bordercolor=LINEA,
                    lightcolor=LINEA, darkcolor=LINEA, insertcolor=TEXTO,
                    padding=(5, 3))
    style.map("TEntry", bordercolor=[("focus", AZUL)],
              lightcolor=[("focus", AZUL)], darkcolor=[("focus", AZUL)])
    style.configure("TCombobox", fieldbackground=BLANCO, background=SUPERFICIE,
                    bordercolor=LINEA, lightcolor=LINEA, darkcolor=LINEA,
                    arrowcolor=TEXTO_SUAVE, padding=(5, 3))
    style.map("TCombobox", fieldbackground=[("readonly", BLANCO)],
              bordercolor=[("focus", AZUL)])
    style.configure("TButton", font=ui(), background=SUPERFICIE,
                    foreground=TEXTO, bordercolor=LINEA, lightcolor=SUPERFICIE,
                    darkcolor=LINEA, focuscolor=SUPERFICIE, padding=(10, 4))
    style.map("TButton", background=[("active", AZUL_SUAVE)],
              bordercolor=[("active", AZUL)])
    style.configure("TRadiobutton", background=SUPERFICIE, foreground=TEXTO,
                    font=ui(), indicatorcolor=BLANCO, focuscolor=SUPERFICIE)
    style.map("TRadiobutton", indicatorcolor=[("selected", AZUL)],
              background=[("active", SUPERFICIE)])
    style.configure("TCheckbutton", background=SUPERFICIE, foreground=TEXTO,
                    font=ui())
    style.configure("TSeparator", background=LINEA)
    style.configure("TScrollbar", troughcolor=FONDO, background=LINEA,
                    bordercolor=FONDO, lightcolor=LINEA, darkcolor=LINEA,
                    arrowcolor=TEXTO_SUAVE, arrowsize=12)
    style.map("TScrollbar", background=[("active", TEXTO_SUAVE)])
    style.configure("TPanedwindow", background=FONDO)
    style.configure("Sash", sashthickness=6, gripcount=0)

    style.configure("Treeview", background=SUPERFICIE, fieldbackground=SUPERFICIE,
                    foreground=TEXTO, font=ui(), rowheight=22,
                    bordercolor=LINEA, lightcolor=SUPERFICIE, darkcolor=LINEA)
    style.configure("Treeview.Heading", background=FONDO, foreground=TEXTO_SUAVE,
                    font=ui(PEQUENA_PT, "bold"), relief="flat",
                    bordercolor=LINEA, padding=(6, 4))
    style.map("Treeview", background=[("selected", AZUL_SUAVE)],
              foreground=[("selected", TEXTO)])
    style.map("Treeview.Heading", background=[("active", FONDO)],
              relief=[("active", "flat"), ("pressed", "flat")])

    style.configure("TNotebook", background=FONDO, borderwidth=0,
                    tabmargins=(0, 0, 0, 0))
    style.configure("TNotebook.Tab", background=FONDO, foreground=TEXTO_SUAVE,
                    font=ui(), padding=(14, 6), borderwidth=0,
                    focuscolor=FONDO)
    style.map("TNotebook.Tab", background=[("selected", SUPERFICIE)],
              foreground=[("selected", TEXTO)],
              expand=[("selected", (0, 0, 0, 0))])

    # EL NOTEBOOK QUE CONMUTA LA NAVEGACION LATERAL (bloque 3): conserva
    # sus pestañas --- `select`, `tabs`, `index` y los cuatro `add` son el
    # contrato que la suite y los apoyos leen --- y NO las pinta: la tira
    # de pestañas se retira por estilo, con un layout vacio para su
    # elemento `Tab`, y el paso activo lo dice la navegacion de al lado.
    style.configure("Lateral.TNotebook", background=FONDO, borderwidth=0,
                    tabmargins=(0, 0, 0, 0))
    style.layout("Lateral.TNotebook.Tab", [])
    # Los items de la navegacion lateral: el inactivo sobre el fondo, el
    # activo sobre superficie, con el numero en la monoespaciada azul.
    style.configure("Nav.TFrame", background=FONDO)
    style.configure("Activo.Nav.TFrame", background=SUPERFICIE)
    style.configure("Nav.TLabel", background=FONDO, foreground=TEXTO_SUAVE,
                    font=ui())
    style.configure("Activo.Nav.TLabel", background=SUPERFICIE, foreground=TEXTO,
                    font=ui(CUERPO_PT, "bold"))
    style.configure("NavNumero.TLabel", background=FONDO, foreground=TEXTO_SUAVE,
                    font=mono(CUERPO_PT, "bold"))
    style.configure("Activo.NavNumero.TLabel", background=SUPERFICIE,
                    foreground=AZUL, font=mono(CUERPO_PT, "bold"))
    return tipo


def texto_plano(master, **kw):
    """
    Un `tk.Text` con la cara del tema: superficie, linea fina, monoespaciada
    del cuerpo de la interfaz. Es el widget de los paneles de detalle y de
    la comparacion; quien lo pide pasa `height`, `wrap` y lo demas.
    """
    opciones = dict(background=SUPERFICIE, foreground=TEXTO, relief="flat",
                    highlightbackground=LINEA, highlightcolor=AZUL,
                    insertbackground=TEXTO, font=tipografia().mono(CUERPO_PT))
    opciones.update(kw)
    return tk.Text(master, highlightthickness=1, padx=8, pady=6, **opciones)


# ---------------------------------------------------------------------------
# Texto en PROSA: para leer, con la tipografia de interfaz y etiquetas con
# nombre (bloque 4 del rediseño visual)
# ---------------------------------------------------------------------------
# Hasta el bloque 4 los paneles de detalle y la ayuda volcaban su contenido
# en un `tk.Text` monoespaciado, rotulo, dos puntos y texto corrido, con
# subrayados de «=» a mano: se leia como una consola. El contenido sigue
# siendo el MISMO (las fichas, las lineas de la CLI); lo que cambia es que
# se escribe con etiquetas --- titulo, seccion, rotulo, cuerpo, sangria,
# suave, mono, aviso --- sobre la tipografia de interfaz, y la monoespaciada
# queda para lo que es codigo o clave. Las tres funciones de escritura de
# abajo eligen etiquetas; no eligen contenido.
ETIQUETAS_DE_PROSA = ("titulo", "seccion", "rotulo", "cuerpo", "sangria",
                      "suave", "mono", "aviso")


def configurar_prosa(texto):
    """Configura las etiquetas de `ETIQUETAS_DE_PROSA` sobre un `tk.Text`."""
    ui, mono = tipografia().ui, tipografia().mono
    texto.tag_configure("titulo", font=ui(CUERPO_PT + 2, "bold"), spacing3=6)
    texto.tag_configure("seccion", font=ui(PEQUENA_PT, "bold"),
                        foreground=TEXTO_SUAVE, spacing1=10, spacing3=2)
    texto.tag_configure("rotulo", font=ui(CUERPO_PT, "bold"), spacing1=8)
    texto.tag_configure("cuerpo", font=ui(CUERPO_PT), spacing3=3)
    texto.tag_configure("sangria", lmargin1=18, lmargin2=18)
    texto.tag_configure("suave", font=ui(PEQUENA_PT), foreground=TEXTO_SUAVE)
    texto.tag_configure("mono", font=mono(PEQUENA_PT))
    texto.tag_configure("aviso", font=ui(CUERPO_PT, "bold"), foreground=AMBAR)


def texto_prosa(master, **kw):
    """
    Un `tk.Text` para LEER: superficie, linea fina, tipografia de interfaz
    y las etiquetas de prosa ya configuradas. Quien lo pide pasa `height`,
    `wrap` y lo demas; el contenido se escribe con `escribir_campos`,
    `escribir_lineas_de_cli` o con `insert` y una etiqueta de la lista.
    """
    opciones = dict(background=SUPERFICIE, foreground=TEXTO, relief="flat",
                    highlightbackground=LINEA, highlightcolor=AZUL,
                    insertbackground=TEXTO, font=tipografia().ui(CUERPO_PT),
                    spacing1=2, spacing3=2)
    opciones.update(kw)
    texto = tk.Text(master, highlightthickness=1, padx=10, pady=8, **opciones)
    configurar_prosa(texto)
    return texto


def escribir_campos(texto, campos, titulo=None):
    """
    Escribe una lista de (rotulo, valor[, etiqueta]) como bloques: el rotulo
    en mayusculas pequeñas y el valor debajo como parrafo. `etiqueta` es la
    del valor (`cuerpo` si no se dice; `aviso` para lo que hay que mirar).
    Un valor vacio no se escribe. El widget vuelve a solo lectura al final.
    """
    texto.configure(state="normal")
    texto.delete("1.0", "end")
    if titulo:
        texto.insert("end", titulo + "\n", "titulo")
    for campo in campos:
        rotulo, valor = campo[0], campo[1]
        etiqueta = campo[2] if len(campo) > 2 else "cuerpo"
        if valor is None or str(valor).strip() == "":
            continue
        texto.insert("end", rotulo.upper() + "\n", "seccion")
        texto.insert("end", str(valor).strip() + "\n", etiqueta)
    texto.configure(state="disabled")


def _es_separador(linea):
    limpia = linea.strip()
    return bool(limpia) and set(limpia) <= {"-", "="}


def escribir_lineas_de_cli(texto, lineas):
    """
    Escribe las lineas que la CLI imprime de un punto (`cli._lineas_punto`)
    con las etiquetas de prosa: los separadores de guiones no se pintan, la
    primera linea es el titulo, una linea que termina en dos puntos es una
    seccion, lo que empieza por `[` (las marcas de veredicto y de bloqueo)
    va en monoespaciada, y la sangria de la CLI se conserva como margen.
    El TEXTO de cada linea es el de la CLI, sin cambiar una palabra.
    """
    texto.configure(state="normal")
    texto.delete("1.0", "end")
    titulo_pendiente = True
    for linea in lineas:
        if _es_separador(linea) or not linea.strip():
            continue
        contenido = linea.strip()
        if titulo_pendiente:
            texto.insert("end", contenido + "\n", "titulo")
            titulo_pendiente = False
            continue
        sangria = len(linea) - len(linea.lstrip(" "))
        etiquetas = ("sangria",) if sangria > len(linea[:sangria]) // 2 + 2 else ()
        if contenido.endswith(":") and not any(ch.isdigit() for ch in contenido):
            texto.insert("end", contenido + "\n", ("seccion",) + etiquetas)
        elif contenido.startswith("["):
            # Los huecos con que la CLI alinea columnas se colapsan: aqui no
            # hay columna que alinear y el hueco se lee como un salto.
            texto.insert("end", re.sub(r" {3,}", "  ", contenido) + "\n",
                         ("mono",) + etiquetas)
        else:
            texto.insert("end", contenido + "\n", ("cuerpo",) + etiquetas)
    texto.configure(state="disabled")


def repartir_al_mostrar(paned):
    """
    Coloca el divisor de un `PanedWindow` de dos paneles segun los PESOS con
    que se añadieron, la primera vez que el widget recibe su tamaño.

    Sin esto el divisor nace donde lo dejan los anchos NATURALES de los dos
    paneles --- y una tabla de doce columnas pide mas ancho que la ventana
    entera ---, de modo que el peso solo repartia el sobrante y la columna
    de la tabla se quedaba con lo que la otra no pedia (medido en el bloque
    2: la columna del filtro nacia en 540 px con el recuento fuera de la
    vista). A partir de la primera colocacion el divisor es del usuario.
    """
    def _colocar(evento):
        paned.unbind("<Configure>", identificador)
        pesos = [int(paned.pane(pane, "weight")) for pane in paned.panes()]
        if len(pesos) != 2 or sum(pesos) <= 0:
            return
        paned.sashpos(0, evento.width * pesos[0] // sum(pesos))
    identificador = paned.bind("<Configure>", _colocar, add="+")


class NavegacionLateral(ttk.Frame):
    """
    La navegacion lateral de pasos numerados que CONMUTA un `Notebook`.

    El Notebook se conserva por debajo (bloque 3 del rediseño visual): sus
    pestañas siguen existiendo y `select`, `tabs`, `index` y `add` siguen
    siendo la puerta que la suite, los apoyos de ventana real y la propia
    ventana usan para cambiar de vista. Lo que cambia es QUIEN LO PINTA:
    la tira de pestañas se retira por estilo (`Lateral.TNotebook`) y esta
    columna muestra un item por pestaña --- numero y titulo, los mismos de
    `VISTAS` --- y marca el activo. Un clic en un item hace `select`; un
    `select` hecho por cualquier otro camino (el clic del anticipo, el
    final de la corrida, un test) llega por `<<NotebookTabChanged>>` y
    repinta el item activo. Una sola fuente del paso activo: el Notebook.
    """

    def __init__(self, master, notebook, titulos):
        super().__init__(master, style="Fondo.TFrame")
        self.notebook = notebook
        self.items = []
        for indice, titulo in enumerate(titulos):
            item = ttk.Frame(self, style="Nav.TFrame", padding=(12, 9))
            item.pack(fill="x", pady=(0, 4))
            numero = ttk.Label(item, text=str(indice + 1), style="NavNumero.TLabel")
            numero.pack(side="left", padx=(0, 10))
            rotulo = ttk.Label(item, text=titulo, style="Nav.TLabel")
            rotulo.pack(side="left")
            for widget in (item, numero, rotulo):
                widget.configure(cursor="hand2")
                widget.bind("<Button-1>", lambda _evt, i=indice: self.ir(i))
            self.items.append((item, numero, rotulo))
        notebook.bind("<<NotebookTabChanged>>", lambda _evt: self.refrescar(),
                      add="+")
        self.refrescar()

    def ir(self, indice):
        """Selecciona la pestaña `indice` (desde 0) en el Notebook."""
        self.notebook.select(self.notebook.tabs()[indice])

    def activo(self):
        """El indice de la pestaña activa, o None si el Notebook esta vacio."""
        try:
            return self.notebook.index("current")
        except tk.TclError:
            return None

    def refrescar(self):
        actual = self.activo()
        for indice, (item, numero, rotulo) in enumerate(self.items):
            prefijo = "Activo." if indice == actual else ""
            item.configure(style=f"{prefijo}Nav.TFrame")
            numero.configure(style=f"{prefijo}NavNumero.TLabel")
            rotulo.configure(style=f"{prefijo}Nav.TLabel")


class Panel(ttk.Frame):
    """
    Panel plano sin borde, sobre superficie, con su titulo en MAYUSCULAS
    pequeñas. El contenido se agrega en `.interior`.

    Es lo que sustituye al `ttk.LabelFrame` de borde y titulo en cuerpo: el
    titulo en mayusculas pequeñas en `TEXTO_SUAVE` es el rotulo de seccion
    del estilo de referencia, y el borde lo pone el CONTRASTE de la
    superficie contra el fondo, no una linea.
    """

    def __init__(self, master, titulo, **kw):
        super().__init__(master, style="Panel.TFrame", **kw)
        self.configure(padding=(12, 8, 12, 10))
        self.titulo = ttk.Label(self, text=titulo.upper(),
                                style="TituloPanel.TLabel")
        self.titulo.pack(anchor="w", pady=(0, 4))
        self.interior = ttk.Frame(self, style="Panel.TFrame")
        self.interior.pack(fill="both", expand=True)


class Insignia(ttk.Label):
    """
    Insignia de estado: texto corto sobre fondo suave, en monoespaciada.

    LLEVA SIEMPRE TEXTO: el estado se lee, y el color lo acompaña. Por eso el
    constructor exige el texto y `configurar` cambia texto y estado en la
    misma llamada; una insignia sin texto seria un estado comunicado solo por
    color.
    """

    def __init__(self, master, texto, estado=INSIGNIA_NEUTRA, **kw):
        super().__init__(master, text=texto, style=estilo_de_insignia(estado),
                         **kw)
        self.estado = estado

    def configurar(self, texto, estado):
        self.estado = estado
        self.configure(text=texto, style=estilo_de_insignia(estado))


class TituloDeVista(ttk.Frame):
    """
    La cabecera de cada pestaña: «PASO n / N» en azul pequeño, el titulo de
    la vista y su subtitulo. Los tres textos los da el llamador; el rotulo
    del paso se ARMA aqui para que las cuatro pestañas lo digan igual.

    Es un `ttk.Frame` --- y no una clase con `pack`/`grid` propios --- para
    que el llamador lo coloque con los geometry managers de Tk, que el
    barrido de literales reconoce; redefinirlos aqui les quitaria a TODAS las
    llamadas `pack` de este archivo la exencion de geometria.
    """

    def __init__(self, master, numero, total, titulo, subtitulo):
        super().__init__(master, style="Fondo.TFrame")
        self.paso = ttk.Label(self, text=f"PASO {numero} / {total}",
                              style="Paso.TLabel")
        self.paso.pack(anchor="w")
        self.titulo = ttk.Label(self, text=titulo, style="Titulo.TLabel")
        self.titulo.pack(anchor="w")
        self.subtitulo = ttk.Label(self, text=subtitulo,
                                   style="Subtitulo.TLabel", justify="left")
        self.subtitulo.pack(anchor="w", pady=(2, 0))


# ---------------------------------------------------------------------------
# El parser GUI-GUI: lo que se teclea en un campo, como valor
# ---------------------------------------------------------------------------
# UN SOLO PARSER PARA LAS DOS VENTANAS (EXT-G-01, PC-13). Hasta EXT-5 la
# pestaña 2 (`ExpedienteApp._interpretar_valor_declarado`) y la emergente
# (`VentanaNormativa._valor_tecleado`) tenian cada una el suyo, y el docstring
# de la segunda decia «misma regla que la pestaña» siendo falso desde C8: la
# pestaña leia un literal estructurado y la emergente no, de modo que
# '[[1.20, 0.90]]' era una lista en un panel y una cadena en el otro. Y los
# dos hacian `float()` sobre TODO lo que parecia numero, de modo que '1' era
# 1.0 en los dos y la GUI no podia declarar el entero que
# `M2.numero_de_celdas` exige (PC-13): desde la ventana, ningun marco pasaba
# de M2.
#
# LA REGLA, en el orden en que se aplica:
#
#   1. vacio                          -> ValueError (SIS-E-04: control de
#                                        flujo del widget, no ErrorProyecto)
#   2. abre con '[', '(' o '{'        -> `ast.literal_eval`; mal cerrado ->
#                                        ValueError (nunca una traza de Tk)
#   3. `[+-]?\d+`                     -> int
#   4. con separador decimal ('.' o ',') o exponente -> float
#   5. parece un numero y no es 3 ni 4 (dos separadores, '1.200,50',
#      '1,000,000', '--1', '1e')      -> ValueError, diciendo la politica
#   6. cualquier otro texto           -> el texto, tal cual (la clave de una
#                                        fila, un metodo, una categoria)
#
# POLITICA DE COMA Y MILES. Se admite la coma DECIMAL, que es como se
# teclea aqui, y por eso '1,5' es 1.5 y '1,200' es 1.2 (el dictamen lo mide y
# no lo cuenta como defecto). NO se admite separador de miles: '1.200,50' no
# es 1200.5 ni 1.2, y leerlo como cualquiera de las dos seria adivinar. Se
# rechaza nombrando la politica.
#
# 'nan', 'inf' e 'Infinity' NO se leen como numero: caen en la regla 6 como
# TEXTO, y la puerta de declaracion los rechaza por su forma (un `float` no
# admite texto) o por `_verificar_finitud`, que lee la cadena. Es lo que da a
# 'nan' EL MISMO VEREDICTO al escribir y al declarar (PC-14): antes
# `float('nan')` tenia exito al teclear y el campo se pintaba de ambar,
# mientras el boton lo rechazaba despues. Un infinito NUMERICO si puede
# salir de aqui --- '1e400' es un real con exponente y `float()` lo desborda
# a inf ---, y lo atrapan las mismas dos guardias: `_verificar_finitud` en la
# puerta y `_como_numero` al escribir, que solo admite finitos.
#
# LA DIVERGENCIA CON LA CLI SE CONSERVA. `cli.declarar_criterios` resuelve
# el texto ENTERO con `ast.literal_eval`, y '1,5' alli no es 1.5: es un
# rechazo explicito desde EXT-1 (PC-34). El parser compartido es GUI-GUI y
# no CLI-GUI, y `tests/test_gui_contrato.py` fija esa divergencia a
# proposito: unificar por el lado de la CLI convertiria la coma decimal en
# tupla en silencio, que es peor que dos parsers.
# `re.ASCII`: sin la bandera, `\d` casa tambien digitos arabes o de ancho
# completo y `int('١')` los acepta en silencio (auditoria adversarial de
# EXT-5). Un numero tecleado aqui son cifras ASCII, y nada mas.
_ENTERO = re.compile(r"^[+-]?\d+$", re.ASCII)
_REAL = re.compile(r"^[+-]?(\d+[.,]\d*|[.,]\d+|\d+)([eE][+-]?\d+)?$", re.ASCII)
_PARECE_NUMERO = re.compile(r"^[+-]?[\d.,eE+-]*\d[\d.,eE+-]*$", re.ASCII)
_ABRE_COLECCION = "[({"

POLITICA_DE_COMA = (
    "se admite la coma decimal ('1,5' es 1.5) y NO se admite separador de "
    "miles ni mas de un separador: '1.200,50' no es 1200.5 ni 1.2, y leerlo "
    "como cualquiera de las dos seria adivinar. Escriba '1200,50' o '1200.50'"
)


def interpretar_texto_declarado(texto):
    """
    Lo que el proyectista teclea en un campo de declaracion, como valor.

    `int` para un entero, `float` solo con separador decimal o exponente,
    la lista/tupla/dict de un literal que abre con delimitador, y el texto
    tal cual para lo que no parece numero. `ValueError` para lo que no se
    puede leer: vacio, literal mal cerrado, o un numero con separador de
    miles o dos separadores (la politica esta en `POLITICA_DE_COMA`).

    El `ValueError` NO es de la taxonomia de `ErrorProyecto`, y es
    deliberado (SIS-E-04): un widget vacio o un literal a medio teclear
    todavia no es un dato del expediente, y los llamadores lo convierten en
    el rotulo rojo del panel a tres lineas de aqui.
    """
    texto = texto.strip()
    if texto == "":
        raise ValueError("El valor no puede quedar vacio.")
    if texto[0] in _ABRE_COLECCION:
        try:
            return ast.literal_eval(texto)
        except (ValueError, SyntaxError, TypeError, MemoryError,
                RecursionError) as exc:
            raise ValueError(
                f"«{texto}» empieza como una lista, tupla o dict y no se "
                f"puede leer como tal ({exc}). Los pares del catalogo del "
                "cajon se escriben asi: [[1.20, 0.90], [1.50, 1.20]]"
            ) from None
    if _ENTERO.match(texto):
        return int(texto)
    if _REAL.match(texto):
        return float(texto.replace(",", "."))
    if _PARECE_NUMERO.match(texto):
        raise ValueError(f"«{texto}» parece un numero y no se puede leer: "
                         f"{POLITICA_DE_COMA}")
    return texto


class Tooltip:
    """Globo de ayuda simple para cualquier widget (patron de legacy/Tc.py)."""

    def __init__(self, widget, texto, retardo=400):  # literal-ok: retardo del tooltip, ms
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
        x = self.widget.winfo_rootx() + 18  # literal-ok: offset del tooltip, px
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6  # literal-ok: offset del tooltip, px
        self._tip = tk.Toplevel(self.widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self._tip, text=self.texto, justify="left", background=BLANCO,
            foreground=TEXTO, relief="solid", borderwidth=1,
            font=tipografia().ui(PEQUENA_PT), padx=8, pady=4,
        ).pack()

    def _ocultar(self, _evt=None):
        self._cancelar()
        if self._tip:
            self._tip.destroy()
            self._tip = None


# 120 es el "notch" estandar de la rueda en Windows: `event.delta` llega en
# multiplos de 120 y hay que dividirlo para obtener las unidades de scroll.
# Es aritmetica del evento, no geometria de widget, y por eso la regla de la
# capa de presentacion no la exime sola: va marcada.
NOTCH_RUEDA = 120   # literal-ok: notch de la rueda, unidades por delta
# En X11 la rueda son dos botones, no un delta.
BOTON_RUEDA_ARRIBA = 4   # literal-ok: numero del boton de X11 para rueda arriba
BOTON_RUEDA_ABAJO = 5   # literal-ok: numero del boton de X11 para rueda abajo


def unidades_de_rueda(*, num, delta):
    """
    Las unidades que hay que desplazar para un evento de rueda, en las tres
    plataformas: negativo hacia arriba (como espera `yview_scroll`).

    Windows: `delta` en multiplos de +-120, sin `num` util. macOS: `delta`
    pequeno (+-1, +-3...), que con la division de Windows daba cero. X11:
    `num` 4 o 5 y `delta` 0. Un delta que no llega al notch vale UNA unidad
    en su sentido: nunca cero, porque un giro de rueda que no mueve nada es
    una rueda rota para el usuario.
    """
    if num == BOTON_RUEDA_ARRIBA:
        return -1
    if num == BOTON_RUEDA_ABAJO:
        return 1
    if not delta:
        return 0
    magnitud = max(1, abs(int(delta)) // NOTCH_RUEDA)
    return -magnitud if delta > 0 else magnitud


class MarcoScroll(ttk.Frame):
    """Contenedor con scroll vertical: el contenido se agrega en `.interior`."""

    def __init__(self, master, fondo=FONDO, estilo_interior="Fondo.TFrame", **kw):
        super().__init__(master, style=estilo_interior, **kw)
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0,
                                background=fondo)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.vbar.pack(side="right", fill="y")

        self.interior = ttk.Frame(self.canvas, padding=14, style=estilo_interior)
        self._id_win = self.canvas.create_window((0, 0), window=self.interior, anchor="nw")

        self.interior.bind("<Configure>", self._ajustar_region)
        self.canvas.bind("<Configure>", self._ajustar_ancho)
        self.canvas.bind("<Enter>", self._activar_rueda)
        self.canvas.bind("<Leave>", self._desactivar_rueda)

    def _ajustar_region(self, _evt=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _ajustar_ancho(self, evt):
        self.canvas.itemconfigure(self._id_win, width=evt.width)

    # LA RUEDA EN LAS TRES PLATAFORMAS (EXT-8, PC-17). Hasta EXT-8 solo se
    # escuchaba `<MouseWheel>` con `delta/120`: en X11 la rueda no llega por
    # ese evento sino como `<Button-4>` (arriba) y `<Button-5>` (abajo), y en
    # macOS `delta` es pequeno (1, 3...) y `int(-1/120)` daba CERO unidades:
    # el marco no se movia. `unidades_de_rueda` normaliza los tres.
    EVENTOS_RUEDA = ("<MouseWheel>", "<Button-4>", "<Button-5>")

    def _activar_rueda(self, _evt=None):
        for evento in self.EVENTOS_RUEDA:
            self.canvas.bind_all(evento, self._rueda)

    def _desactivar_rueda(self, _evt=None):
        for evento in self.EVENTOS_RUEDA:
            self.canvas.unbind_all(evento)

    def _rueda(self, evt):
        if isinstance(evt.widget, (ttk.Treeview, tk.Listbox, tk.Text)):
            return
        self.canvas.yview_scroll(
            unidades_de_rueda(num=getattr(evt, "num", 0),
                              delta=getattr(evt, "delta", 0)), "units")


class CampoValidable:
    """
    Etiqueta + Entry cuyo borde se pinta de rojo o ambar AL ESCRIBIR.

    `validador` recibe el texto tecleado y devuelve `(color, mensaje)`:
    `color=None` significa que el campo esta bien y el borde vuelve a su
    color neutro. La ventana de rango le pasa un validador que llama a
    `declaracion.validar_en_rango`, de modo que el texto que se pinta bajo el
    campo es EL MISMO que decide si la declaracion se acepta -- una
    validacion al teclear y otra al aceptar es la forma de que la ventana diga
    una cosa y el valor declarado sea otra.
    """

    def __init__(self, master, variable, color_neutro, validador=None,
                 ayuda="", unidad=""):
        self.variable = variable
        self.color_neutro = color_neutro
        self.validador = validador
        self.marco = tk.Frame(master, background=color_neutro, padx=2, pady=2)
        self.entry = ttk.Entry(self.marco, textvariable=variable, justify="right")
        self.entry.pack(fill="x", expand=True)
        self.unidad = unidad
        self.mensaje = ""
        self.color = None
        if ayuda:
            Tooltip(self.entry, ayuda)
        self._traza = variable.trace_add("write", self._al_escribir)

    def _al_escribir(self, *_args):
        if self.validador is None:
            return
        self.color, self.mensaje = self.validador(self.variable.get())
        self.marco.configure(background=self.color or self.color_neutro)
        self.al_validar(self.color, self.mensaje)

    def al_validar(self, color, mensaje):
        """Gancho que la ventana sustituye para pintar el mensaje debajo."""

    def marcar(self, hay_error):
        """El `_marcar` de legacy/Tc.py: pinta el borde sin revalidar."""
        self.marco.configure(
            background=COLOR_ERROR if hay_error else self.color_neutro)

    def desconectar(self):
        """
        Suelta la traza de la variable ANTES de destruir el widget (E-B).

        Los editores tipados de la pestaña 2 se montan y desmontan al
        cambiar de criterio, y una traza viva sobre una variable cuyo marco
        ya no existe revienta con `TclError` a la siguiente escritura --- que
        Tk entrega a `report_callback_exception`, o sea a un cuadro modal ---.
        Quien destruye un campo lo desconecta primero.
        """
        if self._traza is not None:
            try:
                self.variable.trace_remove("write", self._traza)
            except tk.TclError:
                pass
            self._traza = None


class BotonAccion:
    """
    Un `tk.Button` que, al apagarse, SIGUE LEYENDOSE Y DICE POR QUE.

    Existe porque en este proyecto un boton apagado es un BLOQUEO, y la regla
    de CLAUDE.md sobre los bloqueos es que se declaran, no se esconden: la
    misma razon por la que un criterio pendiente lanza `CriterioPendienteError`
    en vez de tomar un valor por defecto. Un boton gris sin explicacion es
    exactamente el default silencioso, dibujado.

    Dos cosas que `tk.Button` no hace solo, y que aqui van juntas porque son
    la misma frase dicha dos veces:

    - **Se lee.** El texto apagado se pinta SIEMPRE con
      `COLOR_BOTON_APAGADO_TEXTO`, y el fondo cambia tambien al par de arriba
      en los botones que llevan `fondo` propio --- que son todos menos uno ---.
      Al que no lo lleva no se le toca el fondo, porque el gris de serie de Tk
      ya contrasta con ese texto (6.33:1 medido). Con el comportamiento de
      serie solo cambia el texto, y queda `#a3a3a3` sobre el color vivo del
      boton encendido: 1.30:1 en el peor de los cinco fondos de esta interfaz.
    - **Dice por que.** `deshabilitar(motivo)` guarda el motivo y lo pinta en
      el tooltip, delante de la ayuda permanente del boton. Quien pasa el raton
      por encima lee «no disponible: <motivo>» en vez de adivinar.
    - **Y lo dice a la vista** (EXT-8, PC-17): el tooltip exige un raton
      encima y un lector de pantalla no lo lee. `con_rotulo(master)` crea un
      `ttk.Label` junto al boton que muestra el MISMO motivo mientras el
      boton esta apagado, y se vacia al encenderlo. La ventana lo coloca
      donde quiere; el texto lo pone esta clase, para que rotulo y tooltip
      no puedan decir cosas distintas del mismo bloqueo.

    El tooltip es el `Tooltip` de este mismo archivo --- no se reinventa --- y
    se crea UNA vez: se le reescribe el texto, porque un segundo `Tooltip`
    sobre el mismo widget dejaria dos globos compitiendo por el `<Enter>`.
    """

    # Los tres cuerpos de letra que esta interfaz usa en un boton, PEDIDOS POR
    # NOMBRE. El llamador dice "grande" o "discreta"; el tamano lo pone este
    # archivo. Es lo que se querria de todas formas --- una sola decision sobre
    # como se ve un boton de accion, en el modulo que existe para eso --- y
    # ademas es lo unico que deja la tipografia DENTRO de la llamada al widget,
    # que es donde `tests/test_sin_literales.py` la reconoce como geometria de
    # presentacion y no como un valor de proyecto disfrazado.
    NORMAL = "normal"
    GRANDE = "grande"
    DISCRETA = "discreta"

    def __init__(self, master, texto, *, ayuda="", fondo=None, texto_color="white",
                 motivo=None, letra=NORMAL, **kw):
        self.fondo = fondo
        self.texto_color = texto_color
        self.ayuda = ayuda
        self.motivo = motivo
        opciones = dict(text=texto, relief="flat", cursor="hand2", **kw)
        if fondo is not None:
            opciones.update(bg=fondo, fg=texto_color)
        # Tres llamadas y no una con la fuente en una variable: escrita asi, la
        # tupla es argumento DIRECTO de `tk.Button` en los tres casos.
        tipo = tipografia()
        if letra == self.GRANDE:
            self.boton = tk.Button(master, font=tipo.ui(CUERPO_PT + 1, "bold"), **opciones)
        elif letra == self.DISCRETA:
            self.boton = tk.Button(master, font=tipo.ui(PEQUENA_PT), **opciones)
        else:
            self.boton = tk.Button(master, font=tipo.ui(PEQUENA_PT, "bold"), **opciones)
        self.tooltip = Tooltip(self.boton, ayuda)
        self.rotulo = None
        self._pintar(motivo is None)

    def con_rotulo(self, master, **kw):
        """
        Crea (una vez) el rotulo visible del motivo y lo devuelve para que el
        llamador le haga `pack`/`grid`. Con el boton encendido esta vacio.
        """
        if self.rotulo is None:
            self.rotulo = ttk.Label(master, text="", **kw)
            self._pintar(self.motivo is None)
        return self.rotulo

    # El widget, para quien tenga que hacerle `pack`/`grid`/`config(text=...)`.
    #
    # La guardia no es paranoia: `__getattr__` se llama cuando la busqueda
    # normal falla, y si alguien preguntara por un atributo ANTES de que
    # `self.boton` exista, `self.boton` fallaria tambien y la llamada se
    # llamaria a si misma hasta agotar la pila. Se corta nombrando el caso.
    def __getattr__(self, nombre):
        if nombre == "boton":
            raise AttributeError(nombre)
        return getattr(self.boton, nombre)

    def _pintar(self, encendido):
        if encendido:
            estado, fondo, frente = "normal", self.fondo, self.texto_color
        else:
            estado = "disabled"
            fondo, frente = COLOR_BOTON_APAGADO_FONDO, COLOR_BOTON_APAGADO_TEXTO
        opciones = {"state": estado}
        if self.fondo is not None:
            opciones.update(bg=fondo, fg=frente)
        # `disabledforeground` se fija SIEMPRE, tambien cuando el boton no
        # lleva fondo propio: es el color con que Tk pinta el texto apagado y
        # el defecto (`#a3a3a3`) es justo el que no se lee.
        opciones["disabledforeground"] = COLOR_BOTON_APAGADO_TEXTO
        self.boton.configure(**opciones)
        self.tooltip.texto = self.ayuda if encendido else self._texto_apagado()
        if self.rotulo is not None:
            self.rotulo.configure(
                text="" if encendido else self._motivo_apagado())

    def _motivo_apagado(self):
        return f"No disponible: {self.motivo}" if self.motivo else "No disponible."

    def _texto_apagado(self):
        motivo = self._motivo_apagado()
        return f"{motivo}\n\n{self.ayuda}" if self.ayuda else motivo

    def habilitar(self):
        """Enciende el boton y devuelve el tooltip a su ayuda permanente."""
        self.motivo = None
        self._pintar(True)

    def deshabilitar(self, motivo):
        """Apaga el boton DICIENDO POR QUE. El motivo no es opcional."""
        self.motivo = motivo
        self._pintar(False)

    def estado(self, encendido, motivo):
        """
        `habilitar()` o `deshabilitar(motivo)` segun un booleano.

        `motivo` NO lleva defecto, y es el mismo argumento que en
        `deshabilitar`: con `motivo=""` esta firma dejaba apagar un boton sin
        decir por que --- «No disponible.» a secas ---, o sea justo el bloqueo
        mudo que esta clase existe para impedir. Que el defecto no exista es lo
        que hace cumplible la frase «el motivo no es opcional».
        """
        if encendido:
            self.habilitar()
        else:
            self.deshabilitar(motivo)


class BotonAyuda:
    """
    El icono «i» que abre una ayuda. Pequeño, al lado del campo que explica.

    Es su propio componente y no un `ttk.Button` suelto por una razon de las
    de este archivo: en cuanto haya dos, tienen que verse iguales y comportarse
    igual, y la unica forma de que eso siga siendo verdad dentro de un año es
    que haya UN sitio donde esta escrito como se ve un icono de ayuda.

    NO ES UN `BotonAccion`, y la diferencia no es de tamaño: aquel existe para
    APAGARSE diciendo por que --- un boton apagado es un bloqueo declarado ---
    y este no se apaga nunca. La ayuda de un campo no depende del estado del
    expediente: se puede leer con el campo vacio, que es justamente cuando mas
    falta hace.
    """

    def __init__(self, master, comando, ayuda):
        self.boton = tk.Button(
            master, text="i", command=comando, relief="flat", cursor="hand2",
            width=2, font=tipografia().ui(PEQUENA_PT, "bold"),
            bg=COLOR_AYUDA_FONDO, fg="white", activebackground=COLOR_AYUDA_ACTIVO,
            activeforeground="white")
        self.tooltip = Tooltip(self.boton, ayuda)

    def __getattr__(self, nombre):
        if nombre == "boton":
            raise AttributeError(nombre)
        return getattr(self.boton, nombre)
