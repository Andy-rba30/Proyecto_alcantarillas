# -*- coding: utf-8 -*-
"""
gui/editores.py
===============
Los editores TIPADOS de la pestaña 2 (E-B, E10): un widget por forma de
`Criterio.forma`, construido sobre `gui/componentes.CampoValidable` --- el
campo que valida AL ESCRIBIR --- y con el parser unico de las dos ventanas
(`interpretar_texto_declarado`). Aqui solo se PINTA: que campos tiene cada
editor, de que tipo y con que ventana lo dice `src/editores.py`
(`esquema_de`), y la validacion de cada campo es `src.editores.validar_campo`
sobre lo que el parser devolvio.

Como encajan con la pestaña 2, y por que asi
--------------------------------------------
La pestaña 2 tiene UN solo camino de declaracion desde EXT-5: el campo
literal (`valor_declarado_var`) se interpreta con el parser, pasa la guardia
y entra. Estos editores NO abren un segundo camino: COMPONEN ese literal.
Cada cambio en un campo del editor arma el valor entero y lo escribe en el
literal (`al_cambiar`), y cada valor que llega al literal --- al seleccionar
un criterio, o tecleado a mano --- se descompone en los campos
(`poner_valor`). Dos vistas del mismo valor, una sola fuente; y «aplicar»
sigue leyendo el literal, lo arma entero y lo declara en UNA llamada
(`src.editores.declarar`), o no declara nada.

Por eso este archivo no llama a `declaracion` ni a
`establecer_valor_dinamico`: declarar es de la pestaña, por `src/editores`,
y `tests/test_eb_editores_comparador.py` lo fija por AST (la misma guardia
que `gui/ventana_normativa.py` tiene desde S17).

Lo que cada editor añade sobre el literal: el de tabla ofrece las FILAS y
al elegir una pone su celda y nombra la fila (la seleccion normativa
obtiene el valor de la tabla); el de serie de pares deja añadir y quitar
pares sin escribir corchetes; el de dict pinta un campo por ventana con su
rango; el de par, minimo y maximo; el de serie de claves, una casilla por
fila. El LITERAL es el editor «sin campos» para lo que la ficha no permite
descomponer, y lo dice.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from src import editores as sed
from src.declaracion import Estado
from gui.componentes import (COLOR_AVISO, COLOR_ERROR, COLOR_OK, BotonAccion,
                             CampoValidable, Tooltip,
                             interpretar_texto_declarado)

SEPARADOR_DE_ROTULO = " — "
MOTIVO_SIN_PAR = "escriba los dos numeros del par antes de añadirlo"
MOTIVO_SIN_SELECCION = "seleccione un par de la lista para quitarlo"


def rotulo_de_opcion(opcion) -> str:
    """El texto con que una fila de la tabla se ofrece en el desplegable."""
    texto = f"{opcion.fila}{SEPARADOR_DE_ROTULO}{opcion.etiqueta}"
    if opcion.celdas:
        texto += f"  [{opcion.celdas}]"
    if not opcion.elegible:
        texto += f"  (NO elegible: {opcion.motivo})"
    return texto


def opcion_del_rotulo(esquema, rotulo):
    """La opcion que produjo ese rotulo, o None."""
    for o in esquema.opciones_de_tabla:
        if rotulo_de_opcion(o) == rotulo:
            return o
    return None


def _color_de(resultado):
    if resultado.estado is Estado.INVALIDO:
        return COLOR_ERROR
    if resultado.estado is Estado.AVISO:
        return COLOR_AVISO
    return None


def _texto_de(valor) -> str:
    return "" if valor is None else str(valor)


class EditorTipado:
    """
    La carcasa comun: los campos validables, la fila elegida, la nota, y la
    sincronizacion con el literal de la pestaña (`al_cambiar`).
    """

    def __init__(self, master, esquema, *, color_neutro, al_cambiar):
        self.esquema = esquema
        self.color_neutro = color_neutro
        self.al_cambiar = al_cambiar
        self.marco = ttk.Frame(master)
        self.fila_var = tk.StringVar()
        self.nota_var = tk.StringVar()
        self._sincronizando = False
        self._campos = {}
        self._trazas = []       # (variable, id) de cada traza propia, para desmontar
        self._construir(self.marco)
        self._pie(self.marco)

    def desmontar(self):
        """
        Suelta TODAS las trazas y destruye el marco. Un editor desmontado ya
        no responde a sus variables: la pestaña lo llama antes de montar el
        del siguiente criterio, y una referencia vieja que escriba en sus
        variables no revienta (medido en la ventana real: `TclError` sobre
        un marco destruido, entregado a `report_callback_exception`).
        """
        for cv in self._campos.values():
            if isinstance(cv, CampoValidable):
                cv.desconectar()
        for variable, traza in self._trazas:
            try:
                variable.trace_remove("write", traza)
            except tk.TclError:
                pass
        self._trazas = []
        self.marco.destroy()

    def _trazar(self, variable):
        self._trazas.append((variable, variable.trace_add("write", self._cambio)))

    # -- construccion ----------------------------------------------------
    def _construir(self, p):
        raise NotImplementedError

    def _pie(self, p):
        e = self.esquema
        if e.dominio:
            ttk.Label(p, text=f"Dominio (ficha): {e.dominio}", wraplength=900,
                      justify="left", style="Ayuda.TLabel").pack(anchor="w", pady=(4, 0))
        f_nota = ttk.Frame(p)
        f_nota.pack(fill="x", pady=(4, 0))
        if e.exige_nota:
            rotulo = "Nota = TRAZABILIDAD del ensayo (obligatoria):"
        elif e.exige_fila:
            rotulo = "Nota (procedencia; obligatoria si el valor no proviene de una fila):"
        else:
            rotulo = "Nota (procedencia, opcional):"
        ttk.Label(f_nota, text=rotulo).pack(side="left")
        ent = ttk.Entry(f_nota, textvariable=self.nota_var, width=60)
        ent.pack(side="left", fill="x", expand=True, padx=(6, 0))
        Tooltip(ent, "Viaja con la procedencia y la memoria la imprime. En un\n"
                     "criterio de tabla, un valor que no es el de la celda de la\n"
                     "fila elegida NO entra sin esta nota (EXT-V-02).")

    def _campo_validable(self, master, campo, variable, ayuda=""):
        cv = CampoValidable(
            master, variable, self.color_neutro,
            validador=lambda texto, c=campo: self._validador(c, texto),
            ayuda=ayuda or self._ayuda_de(campo))
        self._trazar(variable)
        self._campos[campo.nombre] = cv
        return cv

    def _ayuda_de(self, campo):
        partes = [f"{campo.nombre}: {campo.tipo}"]
        if campo.rango is not None:
            partes.append(f"ventana de sensibilidad [{campo.rango[0]}, {campo.rango[1]}]")
        if campo.opciones:
            partes.append("opciones: " + ", ".join(campo.opciones))
        return " · ".join(partes)

    def _validador(self, campo, texto):
        texto = texto.strip()
        if not texto:
            r = sed.validar_campo(campo, None)
            return _color_de(r), r.mensaje
        try:
            valor = interpretar_texto_declarado(texto)
        except ValueError as exc:
            return COLOR_ERROR, str(exc)
        r = sed.validar_campo(campo, valor)
        return _color_de(r), r.mensaje

    def _pieza(self, campo, texto):
        """El valor de un campo, o `ValueError` que nombra el campo."""
        texto = texto.strip()
        if not texto:
            if campo.obligatorio:
                raise ValueError(f"falta el campo «{campo.nombre}»")
            return None
        try:
            valor = interpretar_texto_declarado(texto)
        except ValueError as exc:
            raise ValueError(f"«{campo.nombre}»: {exc}") from None
        r = sed.validar_campo(campo, valor)
        if r.estado is Estado.INVALIDO:
            raise ValueError(r.mensaje)
        return valor

    # -- sincronizacion --------------------------------------------------
    def _cambio(self, *_args):
        if not self._sincronizando:
            self.al_cambiar()

    def piezas(self):
        raise NotImplementedError

    def valor(self):
        """El valor ENTERO que los campos componen (ValueError si falta algo)."""
        return sed.armar_valor(self.esquema, self.piezas())

    def poner_valor(self, valor):
        """Los campos desde un valor entero, sin disparar `al_cambiar`."""
        self._sincronizando = True
        try:
            self._poner(sed.descomponer_valor(self.esquema, valor))
        finally:
            self._sincronizando = False

    def _poner(self, piezas):
        raise NotImplementedError

    def fila(self):
        return self.fila_var.get().strip()

    def nota(self):
        return self.nota_var.get().strip()

    def colores(self):
        """El color con que esta pintado cada campo (None = neutro)."""
        return {nombre: cv.color for nombre, cv in self._campos.items()}

    # -- la fila de la tabla ---------------------------------------------
    def _desplegable_de_filas(self, p, al_elegir):
        e = self.esquema
        if not e.opciones_de_tabla:
            return None
        f = ttk.Frame(p)
        f.pack(fill="x", pady=(0, 4))
        ttk.Label(f, text=f"Fila de {e.tabla_id}:").pack(side="left")
        self.rotulo_fila_var = tk.StringVar()
        cmb = ttk.Combobox(f, textvariable=self.rotulo_fila_var, state="readonly",
                           width=70, values=[rotulo_de_opcion(o) for o in e.opciones_de_tabla])
        cmb.pack(side="left", fill="x", expand=True, padx=(6, 0))
        Tooltip(cmb, "Elegir una fila PONE su valor (la celda que el calculo usa,\n"
                     "o la clave de la fila) y la nombra en la procedencia. Las\n"
                     "filas NO elegibles dependen de un dato que el proyecto no\n"
                     "tiene (regla R4) y se rechazan al declarar.")
        cmb.bind("<<ComboboxSelected>>", lambda _e: self._al_elegir_fila(al_elegir))
        self.lbl_fila = ttk.Label(p, text="", style="Ayuda.TLabel")
        self.lbl_fila.pack(anchor="w")
        return cmb

    def _al_elegir_fila(self, al_elegir):
        opcion = opcion_del_rotulo(self.esquema, self.rotulo_fila_var.get())
        if opcion is None:
            return
        self.fila_var.set(opcion.fila)
        self.lbl_fila.config(
            text=f"Fila elegida: {opcion.fila}" + (
                "" if opcion.elegible else f" — NO elegible: {opcion.motivo}"),
            foreground=COLOR_OK if opcion.elegible else COLOR_ERROR)
        al_elegir(opcion)

    def elegir_fila(self, fila):
        """Elige una fila por su clave, como lo haria el raton sobre el desplegable."""
        for o in self.esquema.opciones_de_tabla:
            if o.fila == fila:
                self.rotulo_fila_var.set(rotulo_de_opcion(o))
                self._al_elegir_fila(self._al_fila_elegida)
                return o
        raise KeyError(f"{self.esquema.tabla_id}: no hay fila «{fila}»")

    def _al_fila_elegida(self, opcion):
        """Que hace cada editor con la fila elegida; por defecto, nada."""


class EditorEscalar(EditorTipado):
    """int, float, str, categoria o la union: un campo, y las filas si es de tabla."""

    def _construir(self, p):
        e = self.esquema
        campo = e.campos[0]
        self.var_valor = tk.StringVar()
        # La fila cuya CLAVE lleva el texto ahora mismo (PF-6 b), o None.
        self._fila_que_el_texto_lleva = None
        self.var_valor.trace_add("write", self._soltar_fila_si_el_texto_cambia)
        self._desplegable_de_filas(p, self._al_fila_elegida)
        f = ttk.Frame(p)
        f.pack(fill="x")
        ttk.Label(f, text=f"Valor ({campo.tipo}):").pack(side="left")
        if campo.tipo == sed.TIPO_CATEGORIA:
            cmb = ttk.Combobox(f, textvariable=self.var_valor, state="readonly",
                               values=list(campo.opciones), width=48)
            cmb.pack(side="left", padx=(6, 0))
            Tooltip(cmb, "El conjunto cerrado que la ficha declara en `sensibilidad`.")
            self._trazar(self.var_valor)
            self._campos[campo.nombre] = _CampoSinBorde(self.var_valor, campo)
        else:
            cv = self._campo_validable(f, campo, self.var_valor)
            cv.marco.pack(side="left", fill="x", expand=True, padx=(6, 0))
            if campo.opciones:
                ttk.Label(p, text="Opciones que la ficha nombra: " + "; ".join(campo.opciones),
                          wraplength=900, justify="left", style="Ayuda.TLabel").pack(anchor="w")
        self.lbl_mensaje = ttk.Label(p, text="", wraplength=900, justify="left",
                                     style="Ayuda.TLabel")
        self.lbl_mensaje.pack(anchor="w")
        if campo.nombre in self._campos and isinstance(self._campos[campo.nombre], CampoValidable):
            self._campos[campo.nombre].al_validar = self._mostrar

    def _mostrar(self, color, mensaje):
        self.lbl_mensaje.config(text=mensaje, foreground=color or COLOR_OK)

    def _al_fila_elegida(self, opcion):
        self._fila_que_el_texto_lleva = None
        if opcion.valor_propuesto is not None:
            self.var_valor.set(_texto_de(opcion.valor_propuesto))
        # Solo cuando la fila pone su CLAVE (no una celda) el texto la
        # nombra, y solo entonces reescribirlo la suelta: con una celda
        # (0.5 de la Tabla C.2) otro numero es «DIFIERE de la celda» y la
        # fila tiene que seguir para que la puerta pueda decirlo.
        if isinstance(opcion.valor_propuesto, str) and opcion.valor_propuesto == opcion.fila:
            self._fila_que_el_texto_lleva = opcion

    def _soltar_fila_si_el_texto_cambia(self, *_args):
        """
        Suelta la fila elegida cuando el texto deja de ser su clave (PF-6 b).

        Hasta PF-6 elegir la fila A y reescribir el texto con la clave de B
        dejaba `fila()` en A, y la puerta (`declaracion.declarar_desde_tabla`)
        rechazaba con «el texto NOMBRA la fila B y la procedencia cita la
        fila A». Aqui no se declara nada (guardia por AST de EB-01): solo se
        deja de citar una fila que el texto ya no nombra, y la pestaña 2
        declara la que el texto nombre por `src.editores.fila_implicita`.
        """
        opcion = self._fila_que_el_texto_lleva
        if opcion is None or self._sincronizando:
            return
        if self.var_valor.get().strip() == opcion.fila:
            return
        self._fila_que_el_texto_lleva = None
        self.fila_var.set("")
        if getattr(self, "rotulo_fila_var", None) is not None:
            self.rotulo_fila_var.set("")
        if getattr(self, "lbl_fila", None) is not None:
            self.lbl_fila.config(
                text=f"Fila soltada: el texto ya no es la clave de «{opcion.fila}». "
                     "Se declara lo que el texto nombre (o elija otra fila).",
                foreground=COLOR_AVISO)

    def piezas(self):
        return {sed.CAMPO_UNICO: self._pieza(self.esquema.campos[0], self.var_valor.get())}

    def _poner(self, piezas):
        self.var_valor.set(_texto_de(piezas[sed.CAMPO_UNICO]))


class _CampoSinBorde:
    """El «campo» de un desplegable cerrado: no se pinta, siempre esta bien."""

    def __init__(self, variable, campo):
        self.variable = variable
        self.campo = campo
        self.color = None


class EditorPar(EditorTipado):
    """(minimo, maximo): dos campos con la misma ventana, y las filas si es de tabla."""

    def _construir(self, p):
        self.vars = {n: tk.StringVar() for n in sed.CAMPOS_DEL_PAR}
        self._desplegable_de_filas(p, self._al_fila_elegida)
        f = ttk.Frame(p)
        f.pack(fill="x")
        for campo in self.esquema.campos:
            ttk.Label(f, text=f"{campo.nombre}:").pack(side="left", padx=(0, 4))
            cv = self._campo_validable(f, campo, self.vars[campo.nombre])
            cv.marco.pack(side="left", padx=(0, 12))
            cv.entry.configure(width=12)

    def _al_fila_elegida(self, opcion):
        if isinstance(opcion.valor_propuesto, tuple):
            for n, v in zip(sed.CAMPOS_DEL_PAR, opcion.valor_propuesto):
                self.vars[n].set(_texto_de(v))

    def piezas(self):
        return {c.nombre: self._pieza(c, self.vars[c.nombre].get())
                for c in self.esquema.campos}

    def _poner(self, piezas):
        for n in sed.CAMPOS_DEL_PAR:
            self.vars[n].set(_texto_de(piezas[n]))


class EditorSerieDePares(EditorTipado):
    """
    [(a, b), ...]: la lista de pares en una tabla, y dos campos para añadir
    el siguiente. Sin corchetes ni comas que teclear.
    """

    def _construir(self, p):
        self._pares = []
        self.vars = {n: tk.StringVar() for n in sed.CAMPOS_DE_LA_SERIE}
        f_tabla = ttk.Frame(p)
        f_tabla.pack(fill="x")
        self.tree = ttk.Treeview(f_tabla, columns=sed.CAMPOS_DE_LA_SERIE,
                                 show="headings", height=4)
        for n in sed.CAMPOS_DE_LA_SERIE:
            self.tree.heading(n, text=n)
            self.tree.column(n, width=120, anchor="e")
        self.tree.pack(side="left", fill="x", expand=True)
        Tooltip(self.tree, "Los pares de la serie, en el orden en que se declaran.\n"
                           "El bucle de MD los recorre de menor a mayor.")
        f_alta = ttk.Frame(p)
        f_alta.pack(fill="x", pady=(4, 0))
        for campo in self.esquema.campos:
            ttk.Label(f_alta, text=f"{campo.nombre}:").pack(side="left", padx=(0, 4))
            cv = self._campo_validable(f_alta, campo, self.vars[campo.nombre])
            cv.marco.pack(side="left", padx=(0, 10))
            cv.entry.configure(width=10)
        self.btn_anadir = BotonAccion(
            f_alta, "Añadir par", letra=BotonAccion.DISCRETA, command=self._anadir_fila,
            ayuda="Añade el par (primero, segundo) al final de la serie.")
        self.btn_anadir.pack(side="left", padx=(0, 6))
        self.btn_quitar = BotonAccion(
            f_alta, "Quitar par", letra=BotonAccion.DISCRETA, command=self._quitar_fila,
            ayuda="Quita de la serie el par seleccionado en la tabla.")
        self.btn_quitar.pack(side="left")
        self.lbl_mensaje = ttk.Label(p, text="", wraplength=900, justify="left",
                                     style="Ayuda.TLabel")
        self.lbl_mensaje.pack(anchor="w")

    def _campo_validable(self, master, campo, variable, ayuda=""):
        # Los campos de alta NO componen el literal al escribir: componen
        # al pulsar «Añadir par». Sin esta distincion, teclear «1.2» a
        # medias pisaba la serie entera con un par a medio escribir.
        cv = CampoValidable(
            master, variable, self.color_neutro,
            validador=lambda texto, c=campo: self._validador(c, texto),
            ayuda=ayuda or self._ayuda_de(campo))
        self._campos[campo.nombre] = cv
        return cv

    def _repintar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, (a, b) in enumerate(self._pares):
            self.tree.insert("", "end", iid=str(i), values=(a, b))

    def _anadir_fila(self):
        try:
            par = tuple(self._pieza(c, self.vars[c.nombre].get())
                        for c in self.esquema.campos)
        except ValueError as exc:
            self.lbl_mensaje.config(text=f"No se añadio: {exc}", foreground=COLOR_ERROR)
            return
        self._pares.append(par)
        self._repintar()
        for v in self.vars.values():
            v.set("")
        self.lbl_mensaje.config(text=f"Par {par} añadido: la serie tiene "
                                     f"{len(self._pares)}.", foreground=COLOR_OK)
        self._cambio()

    def _quitar_fila(self):
        seleccion = self.tree.selection()
        if not seleccion:
            self.lbl_mensaje.config(text=MOTIVO_SIN_SELECCION, foreground=COLOR_AVISO)
            return
        indice = int(seleccion[0])
        par = self._pares.pop(indice)
        self._repintar()
        self.lbl_mensaje.config(text=f"Par {par} quitado.", foreground=COLOR_AVISO)
        self._cambio()

    def piezas(self):
        return list(self._pares)

    def _poner(self, piezas):
        self._pares = list(piezas)
        self._repintar()


class EditorDict(EditorTipado):
    """Un campo por clave del dict, con la ventana de cada uno si la ficha la da."""

    def _construir(self, p):
        self.vars = {}
        self._desplegable_de_filas(p, self._al_fila_elegida)
        f = ttk.Frame(p)
        f.pack(fill="x")
        f.columnconfigure(1, weight=1)
        for fila, campo in enumerate(self.esquema.campos):
            var = tk.StringVar()
            self.vars[campo.nombre] = var
            rotulo = campo.nombre + (f"  [{campo.rango[0]}, {campo.rango[1]}]"
                                     if campo.rango is not None else "")
            ttk.Label(f, text=rotulo + ":").grid(row=fila, column=0, sticky="w", padx=(0, 6))
            if campo.tipo == sed.TIPO_CATEGORIA:
                cmb = ttk.Combobox(f, textvariable=var, state="readonly",
                                   values=list(campo.opciones), width=60)
                cmb.grid(row=fila, column=1, sticky="w", pady=1)
                self._trazar(var)
                self._campos[campo.nombre] = _CampoSinBorde(var, campo)
            else:
                cv = self._campo_validable(f, campo, var)
                cv.marco.grid(row=fila, column=1, sticky="we", pady=1)
        self.lbl_mensaje = ttk.Label(p, text="", wraplength=900, justify="left",
                                     style="Ayuda.TLabel")
        self.lbl_mensaje.pack(anchor="w")
        for cv in self._campos.values():
            if isinstance(cv, CampoValidable):
                cv.al_validar = self._mostrar

    def _mostrar(self, color, mensaje):
        self.lbl_mensaje.config(text=mensaje, foreground=color or COLOR_OK)

    def _al_fila_elegida(self, opcion):
        # La fila FIJA sus campos homonimos (K, M, c, Y de la Tabla A.1); los
        # demas se quedan como estan y `declarar` exige la nota si ninguno
        # coincide (auditoria adversarial de E-B, R5).
        if isinstance(opcion.valor_propuesto, dict):
            for campo, celda in opcion.valor_propuesto.items():
                if campo in self.vars:
                    self.vars[campo].set(_texto_de(celda))

    def piezas(self):
        return {c.nombre: self._pieza(c, self.vars[c.nombre].get())
                for c in self.esquema.campos}

    def _poner(self, piezas):
        for c in self.esquema.campos:
            self.vars[c.nombre].set(_texto_de(piezas.get(c.nombre)))


class EditorSerieDeClaves(EditorTipado):
    """Una casilla por fila de la tabla, en el orden de la tabla."""

    def _construir(self, p):
        self.vars = {}
        ttk.Label(p, text=f"Filas de {self.esquema.tabla_id} sobre las que se lee:").pack(anchor="w")
        f = ttk.Frame(p)
        f.pack(fill="x")
        for o in self.esquema.opciones_de_tabla:
            var = tk.BooleanVar(value=False)
            self.vars[o.fila] = var
            # Todas se pueden marcar y desmarcar: la fila NO elegible la
            # rechaza R4 al declarar (por `declarar_desde_tabla`), con su
            # motivo, y una casilla apagada dejaba sin poder DESMARCAR la
            # que el archivo trae (auditoria adversarial de E-B, A2).
            chk = ttk.Checkbutton(f, text=rotulo_de_opcion(o), variable=var)
            chk.pack(anchor="w")
            self._trazar(var)

    def piezas(self):
        claves = [fila for fila, var in self.vars.items() if var.get()]
        if not claves:
            raise ValueError("marque al menos una fila")
        return {sed.CAMPO_CLAVES: claves}

    def _poner(self, piezas):
        marcadas = set(piezas.get(sed.CAMPO_CLAVES, []))
        for fila, var in self.vars.items():
            var.set(fila in marcadas)


class EditorLiteral(EditorTipado):
    """
    El editor SIN campos: la ficha no permite descomponer el valor (un dict
    de dicts, un dict sin ventana ni campos obligatorios) y se escribe
    entero en el campo literal de la pestaña, con el mismo parser y la
    misma guardia. Lo dice, en vez de inventar campos.
    """

    def _construir(self, p):
        ttk.Label(p, text=("Este valor no se descompone en campos desde su ficha "
                           "(ventana por campo, campos obligatorios o un valor de "
                           "escalares): se escribe ENTERO en el campo «Valor nuevo», "
                           "como literal, y pasa la misma guardia."),
                  wraplength=900, justify="left", style="Ayuda.TLabel").pack(anchor="w")
        self._desplegable_de_filas(p, self._al_fila_elegida)

    def piezas(self):
        raise ValueError("el editor literal no compone el valor: se escribe en el campo")

    def _poner(self, piezas):
        """Nada que pintar: el literal ya es la vista."""


EDITOR_POR_TIPO = {
    sed.ESCALAR: EditorEscalar,
    sed.PAR: EditorPar,
    sed.SERIE_DE_PARES: EditorSerieDePares,
    sed.DICT: EditorDict,
    sed.SERIE_DE_CLAVES: EditorSerieDeClaves,
    sed.LITERAL: EditorLiteral,
}


def construir_editor(master, clave, *, color_neutro, al_cambiar):
    """El editor que corresponde a la forma del criterio, montado en `master`."""
    esquema = sed.esquema_de(clave)
    return EDITOR_POR_TIPO[esquema.tipo_de_editor](
        master, esquema, color_neutro=color_neutro, al_cambiar=al_cambiar)
