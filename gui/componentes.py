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
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

COLOR_ERROR = "#e74c3c"
COLOR_AVISO = "#b9770e"
COLOR_OK = "#27ae60"


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
        if isinstance(evt.widget, (ttk.Treeview, tk.Listbox, tk.Text)):
            return
        # 120 es el "notch" estandar de la rueda en Windows: `event.delta`
        # llega en multiplos de 120 y hay que dividirlo para obtener las
        # unidades de scroll. Es aritmetica del evento, no geometria de
        # widget, y por eso la regla de la capa de presentacion no la exime
        # sola: va marcada.
        self.canvas.yview_scroll(int(-evt.delta / 120), "units")  # literal-ok: notch de la rueda, unidades por delta


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
