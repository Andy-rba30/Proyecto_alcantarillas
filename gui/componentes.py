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
import tkinter as tk
from tkinter import ttk

COLOR_ERROR = "#e74c3c"
COLOR_AVISO = "#b9770e"
COLOR_OK = "#27ae60"

# El par del boton DESHABILITADO. No es estetica: es que un boton apagado
# tiene que poder LEERSE, porque su texto es lo unico que dice que haria si
# estuviera encendido.
#
# `tk.Button` no cambia su fondo al deshabilitarse --- solo pinta el texto con
# `disabledforeground`, que por defecto es `#a3a3a3` ---, de modo que el texto
# apagado queda sobre el MISMO color vivo del boton encendido. Medido sobre la
# ventana real, con los cinco fondos que este proyecto usa, el contraste que
# salia era de 1.30:1 a 2.33:1 (el peor, `#a3a3a3` sobre el verde `#16a085` de
# los botones de exportacion). El minimo legible es 4.5:1. Con este par sale
# 6.93:1, y el fondo apagado ademas se DISTINGUE del encendido, que es la otra
# mitad de la senal.
# El azul del icono de ayuda «i». Es el mismo tono del boton de EJECUTAR de la
# ventana principal: un icono de ayuda no compite con la accion, la acompaña.
COLOR_AYUDA_FONDO = "#2e86c1"
COLOR_AYUDA_ACTIVO = "#21618c"

COLOR_BOTON_APAGADO_FONDO = "#dfe3e6"
COLOR_BOTON_APAGADO_TEXTO = "#3d4b59"


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
            self._tip, text=self.texto, justify="left", background="#ffffe0",
            relief="solid", borderwidth=1, font=("Segoe UI", 8), padx=6, pady=3,
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
        if letra == self.GRANDE:
            self.boton = tk.Button(master, font=("Segoe UI", 10, "bold"), **opciones)
        elif letra == self.DISCRETA:
            self.boton = tk.Button(master, font=("Segoe UI", 9), **opciones)
        else:
            self.boton = tk.Button(master, font=("Segoe UI", 9, "bold"), **opciones)
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
            width=2, font=("Segoe UI", 9, "bold"),
            bg=COLOR_AYUDA_FONDO, fg="white", activebackground=COLOR_AYUDA_ACTIVO,
            activeforeground="white")
        self.tooltip = Tooltip(self.boton, ayuda)

    def __getattr__(self, nombre):
        if nombre == "boton":
            raise AttributeError(nombre)
        return getattr(self.boton, nombre)
