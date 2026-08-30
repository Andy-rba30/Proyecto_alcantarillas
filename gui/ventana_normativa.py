# -*- coding: utf-8 -*-
"""
gui/ventana_normativa.py
========================
LA VENTANA. Un solo componente con cuatro caras, de las Sec. 4.2 y 4.3 de
`docs/hoja_de_ruta_correcciones_v12.md`.

Este archivo PINTA. No sabe nada de normas: todo lo que muestra se lo da
`src/ventana_normativa.py`, que lo lee del registro normativo, y todo lo que
declara pasa por `src/declaracion.py`, que a su vez pasa por
`criterios_adoptados.establecer_valor_dinamico`. Aqui no hay ni una cita, ni
un numeral, ni un numero de norma: si algo de eso hiciera falta en pantalla y
no estuviera, el sitio donde arreglarlo es `src/normativa/`.

El reparto es deliberado y es lo que hace que la ventana sea comprobable. El
contenido -- que la Tabla N 10 se titula con «(m/s)», que las dos velocidades
de su fila son maximos, que la columna NORMAL va atenuada y por que -- se
compara campo a campo en `tests/test_ventana_normativa.py`, sin escritorio.
Lo que queda aqui es el cableado de widgets, que es lo unico que de verdad
necesita una pantalla.

El orden visual
---------------
`ventana_normativa.ORDEN_VISUAL_TABLA` declara el orden que pide el plan y un
test lo fija. `_pintar_tabla` recorre ESE orden, de modo que cambiarlo obliga
a cambiar el dato y no solo el codigo:

    1. Titulo literal de la tabla, CON unidades.
    2. Numeral · nombre completo de la norma · edicion · pagina impresa.
    3. La tabla COMPLETA. Las columnas que el calculo no usa: atenuadas.
    4. La condicion de aplicacion de cada fila.
    5. Las notas al pie, integras.
    6. Los modificadores, con su cita.
    7. La cita textual del parrafo que sostiene la tabla.

Reutiliza `gui/componentes.py`, que es `legacy/Tc.py` movido a un modulo comun.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import tkinter as tk
from tkinter import messagebox, ttk

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"
for _ruta in (RAIZ, SRC):
    if str(_ruta) not in sys.path:
        sys.path.insert(0, str(_ruta))

import declaracion as dec  # noqa: E402
import ventana_normativa as vn  # noqa: E402
from gui.componentes import (COLOR_AVISO, COLOR_ERROR, COLOR_OK,  # noqa: E402
                             CampoValidable, MarcoScroll, Tooltip)

# Los rotulos de la carcasa. Son texto de pantalla, no valores de proyecto:
# lo que la ventana AFIRMA sobre una norma sale siempre del registro.
TITULO_POR_CARA = {
    vn.Cara.TABLA: "Tabla normativa - elegir la fila que aplica",
    vn.Cara.RANGO: "Valor acotado por una fuente - rango y semantica",
    vn.Cara.CATALOGO: "Catalogo de proveedor - NO es una norma",
    vn.Cara.CAMPO: "Valor de campo",
}

AVISO_R1 = (
    "La TABLA es normativa [N]. LA ELECCION DE FILA NO LO ES: elegir una fila "
    "no convierte la eleccion en norma. Lo que esta ventana declara es un "
    "criterio [A] cuyo valor PROVIENE de la fila elegida, y asi lo escribe la "
    "memoria: con la fila, la cita, las alternativas descartadas y la fecha."
)

# Las tres fuentes de la ventana. Se nombran porque el barrido de literales de
# la capa de presentacion exime el entero que es argumento DIRECTO de una
# llamada de widget, y un tamano dentro de un condicional no lo es. Nombrarlas
# es ademas lo que se querria de todas formas: tres nombres en vez de la misma
# tupla repetida veinte veces.
FUENTE_CUERPO = ("Segoe UI", 9)             # literal-ok: cuerpo de letra, pt
FUENTE_NEGRITA = ("Segoe UI", 9, "bold")    # literal-ok: cuerpo de letra, pt
FUENTE_TITULO = ("Segoe UI", 11, "bold")    # literal-ok: cuerpo de letra, pt

AVISO_CATALOGO = (
    "Este valor NO tiene numeral y no puede sostener una cita. Un catalogo no "
    "es una fuente normativa, y el descarte de material que produce es de "
    "catalogo, no de norma."
)


class VentanaNormativa(tk.Toplevel):
    """
    La ventana emergente de UNA variable de entrada.

    `al_declarar` es el aviso que la ventana principal recibe cuando algo se
    declara, para refrescar su tabla. Se pasa como parametro y no se busca en
    el padre: una ventana que llamara a metodos de `ExpedienteApp` por su
    nombre no se podria abrir desde ningun otro sitio.
    """

    def __init__(self, master, clave, al_declarar=None):
        super().__init__(master)
        self.clave = clave
        self.al_declarar = al_declarar
        self.ventana = vn.ventana(clave)
        self.valor_var = tk.StringVar()
        self.fila_var = tk.StringVar()
        self.columna_var = tk.StringVar()
        self.campo = None
        self._tree = None

        self.title(f"{clave} - {TITULO_POR_CARA[self.ventana.cara]}")
        self.geometry("1080x760")
        self.minsize(820, 560)
        self.transient(master)

        try:
            self.color_neutro = ttk.Style().lookup("TFrame", "background") \
                or "SystemButtonFace"
        except tk.TclError:
            self.color_neutro = "SystemButtonFace"

        self._construir()

    # ------------------------------------------------------------------
    # Carcasa
    # ------------------------------------------------------------------
    def _construir(self):
        marco = MarcoScroll(self)
        marco.pack(fill="both", expand=True)
        p = marco.interior

        self._cabecera(p)
        pintar = {
            vn.Cara.TABLA: self._pintar_tabla,
            vn.Cara.RANGO: self._pintar_rango,
            vn.Cara.CATALOGO: self._pintar_catalogo,
            vn.Cara.CAMPO: self._pintar_campo,
        }[self.ventana.cara]
        pintar(p)
        self._pie(p)

    def _cabecera(self, p):
        v = self.ventana
        ttk.Label(p, text=f"[{v.etiqueta}] {v.clave}",
                  font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self._parrafo(p, v.concepto, negrita=True)
        self._parrafo(p, f"Unidad: {v.unidad}   ·   Modo de resolucion: "
                         f"{v.modo}   ·   Poblacion: {v.poblacion}   ·   "
                         f"{v.fase}")
        if v.consumido_por:
            self._parrafo(p, "Lo consume: " + ", ".join(v.consumido_por))
        valor = ("(sin declarar)" if v.valor_efectivo is None
                 else repr(v.valor_efectivo))
        marca = " [declarado para esta corrida, no en archivo]" \
            if v.declarada_en_caliente else ""
        ttk.Label(p, text=f"Valor efectivo: {valor}{marca}",
                  font=("Consolas", 10, "bold")).pack(anchor="w", pady=6)
        if v.justificacion:
            self._parrafo(p, f"Justificacion declarada: {v.justificacion}")
        if v.fuente:
            self._parrafo(p, f"Fuente declarada: {v.fuente}")
        procedencia = dec.procedencia_de(self.clave)
        if procedencia is not None:
            self._aviso(p, "PROCEDENCIA REGISTRADA EN ESTA CORRIDA",
                        procedencia.como_texto(), COLOR_OK)
        ttk.Separator(p, orient="horizontal").pack(fill="x", pady=8)

    # ------------------------------------------------------------------
    # Cara TABLA
    # ------------------------------------------------------------------
    def _pintar_tabla(self, p):
        for bloque in self.ventana.tabla.orden_visual:
            getattr(self, f"_bloque_{bloque}")(p, self.ventana.tabla)
        for extra in self.ventana.tablas[1:]:
            ttk.Separator(p, orient="horizontal").pack(fill="x", pady=10)
            self._parrafo(p, "Esta eleccion se lee sobre DOS tablas a la vez: "
                             "la segunda va entera a continuacion.",
                          negrita=True)
            for bloque in extra.orden_visual:
                getattr(self, f"_bloque_{bloque}")(p, extra)

    def _bloque_titulo_literal(self, p, t):
        ttk.Label(p, text=t.titulo_literal, font=("Segoe UI", 11, "bold"),
                  wraplength=980, justify="left").pack(anchor="w")

    def _bloque_linea_de_cita(self, p, t):
        self._parrafo(p, t.linea_de_cita)
        self._parrafo(p, f"Caracter de la fuente: {t.cita.caracter}   ·   "
                         f"{t.rotulo_de_completitud}")
        self._parrafo(p, t.alcance)
        if t.fuente_declarada_por_la_tabla:
            self._parrafo(p, "La tabla declara su propia fuente: "
                             f"{t.fuente_declarada_por_la_tabla}")

    def _bloque_tabla_completa(self, p, t):
        if t.encabezados_superiores:
            self._parrafo(p, "Encabezados superiores: "
                             + " > ".join(t.encabezados_superiores))
        marco = ttk.Frame(p)
        marco.pack(fill="both", expand=True, pady=6)
        columnas = ("fila", *[c.id for c in t.columnas])
        tree = ttk.Treeview(marco, columns=columnas, show="headings", height=12)
        tree.heading("fila", text="FILA (como la imprime la fuente)")
        tree.column("fila", width=320, anchor="w")
        for c in t.columnas:
            unidad = f" [{c.unidad}]" if c.unidad else ""
            apagada = "  (atenuada)" if c.atenuada else ""
            tree.heading(c.id, text=f"{c.etiqueta_literal}{unidad}{apagada}")
            tree.column(c.id, width=150, anchor="center")
        tree.tag_configure("atenuada", foreground="#999999")
        tree.tag_configure("no_elegible", background="#fdecea",
                           foreground=COLOR_ERROR)
        for f in t.filas:
            tags = []
            if not f.elegible:
                tags.append("no_elegible")
            elif f.atenuada:
                tags.append("atenuada")
            marcas = f" ({', '.join(f.llamadas_a_nota)})" \
                if f.llamadas_a_nota else ""
            tree.insert("", "end", iid=f.id, values=(
                f.etiqueta_legible + marcas,
                *[f.celdas.get(c.id, "") for c in t.columnas]), tags=tuple(tags))
        tree.pack(side="left", fill="both", expand=True)
        barra = ttk.Scrollbar(marco, orient="vertical", command=tree.yview)
        tree.configure(yscroll=barra.set)
        barra.pack(side="left", fill="y")
        tree.bind("<<TreeviewSelect>>", self._al_elegir_fila)
        if self._tree is None:
            self._tree = tree

        self._parrafo(p, "Todas las filas y todas las columnas que la fuente "
                         "imprime estan aqui. Las que el calculo NO usa se "
                         "muestran atenuadas, con la razon debajo: una tabla "
                         "podada no es la tabla.")
        for c in t.columnas:
            if c.atenuada:
                self._parrafo(p, f"   Columna «{c.etiqueta_literal}»: "
                                 f"{c.motivo}")
        if t.interpretacion_del_proyectista:
            self._aviso(p, "INTERPRETACION DEL PROYECTISTA",
                        t.interpretacion_del_proyectista, COLOR_AVISO)
        for errata in t.erratas:
            self._aviso(p, "ERRATA / DISCREPANCIA DECLARADA", errata,
                        COLOR_AVISO)
        for afirmacion in t.afirmaciones_negativas:
            self._aviso(p, "LO QUE LA TABLA NO DICE", afirmacion, COLOR_AVISO)
        for laguna in t.lagunas:
            self._aviso(p, "LAGUNA DE LA FUENTE", laguna, COLOR_AVISO)

    def _bloque_condiciones_de_fila(self, p, t):
        con_condicion = [f for f in t.filas
                         if f.condiciones or not f.elegible
                         or f.disponibilidad.resuelta_por]
        if not con_condicion:
            self._parrafo(p, "Ninguna fila de esta tabla cuelga de una "
                             "condicion de aplicacion.")
            return
        ttk.Label(p, text="Condicion de aplicacion de cada fila",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 2))
        for f in con_condicion:
            for texto in f.condiciones:
                self._parrafo(p, f"   {f.etiqueta_legible}: «{texto}»")
            self._pintar_disponibilidad(p, f.etiqueta_legible, f.disponibilidad)

    def _pintar_disponibilidad(self, p, quien, disponibilidad):
        if isinstance(disponibilidad, vn.PideDato):
            self._aviso(
                p, f"FALTA UN DATO PARA «{quien}»",
                f"Condicion {disponibilidad.condicion_id}: "
                f"«{disponibilidad.texto_de_la_condicion}». Hay que declarar "
                f"'{disponibilidad.clave_que_falta}' "
                f"({disponibilidad.concepto_de_lo_que_falta}). Esta ventana "
                "NO elige por usted: hasta que ese criterio tenga valor, la "
                "fila no se puede elegir.", COLOR_AVISO)
        elif isinstance(disponibilidad, vn.BloqueaLaEleccion):
            self._aviso(
                p, f"BLOQUEADA: «{quien}»",
                f"Condicion {disponibilidad.condicion_id}: "
                f"«{disponibilidad.texto_de_la_condicion}». "
                f"{disponibilidad.por_que}. Lo cerraria: "
                f"{disponibilidad.que_lo_cerraria}.", COLOR_ERROR)
        elif disponibilidad.resuelta_por:
            self._parrafo(p, f"   {quien}: elegible ({disponibilidad.resuelta_por})")

    def _bloque_notas_al_pie(self, p, t):
        if not t.notas_al_pie:
            return
        ttk.Label(p, text="Notas al pie de la tabla, integras",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 2))
        for nota in t.notas_al_pie:
            self._parrafo(p, f"   ({nota.marca}) {nota.texto}")

    def _bloque_modificadores(self, p, t):
        if not t.modificadores:
            return
        ttk.Label(p, text="Modificadores que la fuente aplica sobre esta tabla",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 2))
        for m in t.modificadores:
            self._parrafo(p, f"   {m.concepto} - {m.sobre_que}", negrita=True)
            self._parrafo(p, f"      Texto literal: «{m.texto_literal}»")
            self._parrafo(p, f"      Cita: {m.cita}")
            self._parrafo(p, f"      Orden de aplicacion: {m.orden} "
                             "(este campo puede invertir que norma gobierna)")
            for etiqueta, factor, disponibilidad in m.tramos:
                self._parrafo(p, f"      · {etiqueta}  ->  x{factor}")
                self._pintar_disponibilidad(p, etiqueta, disponibilidad)
            if m.piso:
                self._parrafo(p, f"      Piso del modificador: {m.piso}")
            if m.tope:
                self._parrafo(p, f"      Tope del modificador: {m.tope}")
            for laguna in m.lagunas:
                self._aviso(p, "LAGUNA DE LA FUENTE EN EL MODIFICADOR",
                            laguna, COLOR_AVISO)

    def _bloque_cita_textual(self, p, t):
        ttk.Label(p, text="Cita textual que sostiene la tabla",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 2))
        if t.texto_previo:
            self._parrafo(p, f"   Parrafo previo: «{t.texto_previo}»")
        self._parrafo(p, f"   «{t.cita_textual}»")
        self._parrafo(p, f"   {t.cita.linea}")
        if not t.cita.verificada:
            self._aviso(p, "CITA NO VERIFICADA CONTRA EL PDF",
                        "El registro no lleva firma de verificacion para esta "
                        "cita.", COLOR_AVISO)

    def _al_elegir_fila(self, _evt=None):
        seleccion = self._tree.selection() if self._tree else ()
        if not seleccion:
            return
        self.fila_var.set(seleccion[0])
        contenido = self.ventana.tabla
        columna = self.ventana.columna_declarada or self._columna_unica(contenido)
        if columna is None:
            return
        try:
            propuesto = dec.valor_propuesto(contenido.tabla_id,
                                            seleccion[0], columna)
        except KeyError:
            return
        self.valor_var.set(str(propuesto))

    def _columna_unica(self, contenido):
        """
        La columna de valores cuando la tabla trae una sola. Con mas de una, la
        ventana NO propone: proponer significaria elegir la columna por el
        usuario, que es lo que la regla R4 prohibe.
        """
        candidatas = [c.id for c in contenido.columnas if not c.atenuada
                      and c.usada_por]
        return candidatas[0] if len(candidatas) == 1 else None

    # ------------------------------------------------------------------
    # Cara RANGO
    # ------------------------------------------------------------------
    def _pintar_rango(self, p):
        r = self.ventana.rango
        ttk.Label(p, text=r.titulo_de_la_tabla, font=("Segoe UI", 11, "bold"),
                  wraplength=980, justify="left").pack(anchor="w")
        self._parrafo(p, f"Fila: {r.fila_legible}   ·   Columna: {r.columna_id}")
        self._parrafo(p, f"Que acota: {r.que_acota}")

        self._bloque_de_rango(p, "RANGO NORMATIVO - lo que la fuente escribe",
                              r.rango_normativo,
                              extra=f"Semantica (tipo del registro): {r.semantica}")
        if r.dominio_fisico is not None:
            self._bloque_de_rango(
                p, "DOMINIO FISICO - NO es normativo", r.dominio_fisico)
        if r.rango_de_sensibilidad is not None:
            self._bloque_de_rango(
                p, "RANGO DE SENSIBILIDAD - adopcion del proyectista",
                r.rango_de_sensibilidad)
        self._parrafo(p, "Los tres bloques de arriba NO significan lo mismo y "
                         "no se mezclan: uno lo escribe la norma, otro dice "
                         "cuando la celda esta mal llenada, y el tercero es lo "
                         "que el proyectista movio para defender su adopcion "
                         "(Sec. 4.2 del plan).")
        if r.interpretacion_del_proyectista:
            self._aviso(p, "INTERPRETACION DEL PROYECTISTA",
                        r.interpretacion_del_proyectista, COLOR_AVISO)

    def _bloque_de_rango(self, p, titulo, rango, extra=""):
        ttk.Label(p, text=titulo, font=("Segoe UI", 10, "bold")).pack(
            anchor="w", pady=(8, 2))
        self._parrafo(p, f"   {rango.frase}")
        self._parrafo(p, f"   {rango.rotulo}")
        if extra:
            self._parrafo(p, f"   {extra}")
        if rango.unidad:
            self._parrafo(p, f"   Unidad: {rango.unidad}")
        if rango.cita:
            self._parrafo(p, f"   {rango.cita}")
        if rango.que_pasa_fuera:
            self._parrafo(p, f"   Si el valor se sale: {rango.que_pasa_fuera}")

    def _validador_de_rango(self, texto):
        """
        Valida AL ESCRIBIR, con la MISMA funcion que decide al aceptar.

        Devuelve `(color, mensaje)`. Un campo vacio no es un error todavia: es
        un campo que el usuario esta empezando a llenar.
        """
        if not texto.strip():
            return (None, "")
        try:
            valor = float(texto.replace(",", "."))
        except ValueError:
            return (COLOR_ERROR,
                    "Este valor esta acotado por un rango que una fuente "
                    "escribe: hace falta un numero.")
        resultado = dec.validar_en_rango(self.clave, valor)
        color = {dec.Estado.VALIDO: None, dec.Estado.AVISO: COLOR_AVISO,
                 dec.Estado.INVALIDO: COLOR_ERROR}[resultado.estado]
        return (color, resultado.mensaje)

    # ------------------------------------------------------------------
    # Cara CATALOGO
    # ------------------------------------------------------------------
    def _pintar_catalogo(self, p):
        c = self.ventana.catalogo
        self._aviso(p, "ESTO NO ES UNA NORMA", AVISO_CATALOGO, COLOR_ERROR)
        ttk.Label(p, text=c.titulo, font=("Segoe UI", 11, "bold"),
                  wraplength=980, justify="left").pack(anchor="w")
        self._parrafo(p, f"Catalogo: {c.catalogo_id}   ·   Ambito: "
                         f"{c.proveedor_o_ambito}")
        self._parrafo(p, f"Que elige: {c.que_elige}")
        self._aviso(p, "QUE NORMA NO LO SOSTIENE", c.que_norma_NO_lo_sostiene,
                    COLOR_ERROR)
        self._aviso(p, "ADVERTENCIA OBLIGATORIA", c.advertencia, COLOR_ERROR)
        self._parrafo(p, c.sin_numeral)

    # ------------------------------------------------------------------
    # Cara CAMPO
    # ------------------------------------------------------------------
    def _pintar_campo(self, p):
        c = self.ventana.campo
        self._parrafo(p, c.que_pide, negrita=True)
        if c.que_lo_fija:
            self._parrafo(p, f"Lo fija: {c.que_lo_fija}")
        if c.opciones:
            self._parrafo(p, "Opciones declaradas: " + ", ".join(c.opciones))
        if c.ensayo:
            self._parrafo(p, f"Procedimiento: {c.ensayo}")
        if c.trazabilidad_exigida:
            self._aviso(p, "TRAZABILIDAD OBLIGATORIA", c.trazabilidad_exigida,
                        COLOR_AVISO)
        if c.se_deriva_de:
            self._parrafo(p, "Se deriva de: " + ", ".join(c.se_deriva_de))
            self._parrafo(p, f"Regla: {c.regla_de_derivacion}")
        if c.dominio_fisico is not None:
            self._bloque_de_rango(p, "DOMINIO FISICO - NO es normativo",
                                  c.dominio_fisico)
        if c.rango_de_sensibilidad is not None:
            self._bloque_de_rango(
                p, "RANGO DE SENSIBILIDAD - adopcion del proyectista",
                c.rango_de_sensibilidad)
        if c.tabla_pendiente:
            self._aviso(p, "TABLA PENDIENTE DE TRANSCRIBIR",
                        "Esta variable seria `de_tabla` el dia que se "
                        f"transcriba al registro: {c.tabla_pendiente}",
                        COLOR_AVISO)

    # ------------------------------------------------------------------
    # Pie: declarar
    # ------------------------------------------------------------------
    def _pie(self, p):
        ttk.Separator(p, orient="horizontal").pack(fill="x", pady=10)
        v = self.ventana
        if v.cara is vn.Cara.TABLA:
            self._aviso(p, "REGLA R1 DEL PLAN", AVISO_R1, COLOR_AVISO)
        if not v.declarable_aqui:
            self._aviso(p, "ESTA VARIABLE NO SE DECLARA DESDE AQUI",
                        v.por_que_no_declarable, COLOR_ERROR)
            return
        if v.cara is vn.Cara.CAMPO and not v.campo.editable:
            self._aviso(p, "NO EDITABLE",
                        "La calcula el programa desde otras variables ya "
                        "declaradas.", COLOR_AVISO)
            return

        marco = ttk.LabelFrame(p, text="Declarar el valor para esta corrida",
                               padding=10)
        marco.pack(fill="x", pady=6)
        marco.columnconfigure(1, weight=1)

        ttk.Label(marco, text="Valor:").grid(row=0, column=0, sticky="w",
                                             padx=6, pady=6)
        validador = (self._validador_de_rango if v.cara is vn.Cara.RANGO
                     else None)
        self.campo = CampoValidable(
            marco, self.valor_var, self.color_neutro, validador=validador,
            ayuda="Numero (admite coma decimal) o texto, segun lo que pida el "
                  "criterio.")
        self.campo.marco.grid(row=0, column=1, sticky="we", padx=6, pady=6)
        self.lbl_validacion = ttk.Label(marco, text="", wraplength=820,
                                        justify="left")
        self.lbl_validacion.grid(row=1, column=0, columnspan=2, sticky="w",
                                 padx=6)
        self.campo.al_validar = self._mostrar_validacion

        if v.cara is vn.Cara.TABLA:
            ttk.Label(marco, text="Fila elegida:").grid(row=2, column=0,
                                                        sticky="w", padx=6)
            ent_fila = ttk.Entry(marco, textvariable=self.fila_var)
            ent_fila.grid(row=2, column=1, sticky="we", padx=6, pady=4)
            Tooltip(ent_fila, "Se llena al pulsar una fila de la tabla de "
                              "arriba. La procedencia que se registra la "
                              "nombra.")
            ttk.Label(marco, text="Columna elegida:").grid(row=3, column=0,
                                                           sticky="w", padx=6)
            ent_col = ttk.Entry(marco, textvariable=self.columna_var)
            ent_col.grid(row=3, column=1, sticky="we", padx=6, pady=4)
            Tooltip(ent_col, "Solo cuando lo que se elige es una COLUMNA de la "
                             "tabla y no una fila.")

        boton = tk.Button(marco, text="Declarar para esta corrida",
                          font=("Segoe UI", 9, "bold"), bg="#2e86c1",
                          fg="white", relief="flat", cursor="hand2",
                          command=self._declarar)
        boton.grid(row=4, column=0, columnspan=2, sticky="w", padx=6, pady=8,
                   ipadx=8, ipady=3)
        Tooltip(boton, "Pasa por criterios_adoptados.establecer_valor_dinamico,\n"
                       "la misma guardia que el archivo. criterios_adoptados.py\n"
                       "NO se modifica: escribirlo es una accion aparte, desde\n"
                       "la pestana de criterios.")

        self.lbl_estado = ttk.Label(marco, text="", wraplength=820,
                                    justify="left")
        self.lbl_estado.grid(row=5, column=0, columnspan=2, sticky="w", padx=6)

    def _mostrar_validacion(self, color, mensaje):
        self.lbl_validacion.config(text=mensaje,
                                   foreground=color or COLOR_OK)

    def _valor_tecleado(self):
        """
        El texto del campo como valor. Misma regla que la pestana de criterios
        de `gui/app.py`: numero si lo parece -- admitiendo la coma decimal, que
        es como se teclea aqui -- y el texto tal cual si no.
        """
        texto = self.valor_var.get().strip()
        if texto == "":
            raise ValueError("El valor no puede quedar vacio.")
        try:
            return float(texto.replace(",", "."))
        except ValueError:
            return texto

    def _declarar(self):
        try:
            valor = self._valor_tecleado()
            procedencia = self._declarar_segun_cara(valor)
        except (ValueError, KeyError) as exc:
            self.lbl_estado.config(text=f"No se declaro: {exc}",
                                   foreground=COLOR_ERROR)
            return
        self.lbl_estado.config(
            text=f"Declarado para esta corrida. {procedencia.como_texto()}",
            foreground=COLOR_OK)
        if self.al_declarar is not None:
            self.al_declarar(self.clave)

    def _declarar_segun_cara(self, valor):
        cara = self.ventana.cara
        if cara is vn.Cara.TABLA:
            fila = self.fila_var.get().strip()
            columna = self.columna_var.get().strip()
            if not fila and not columna:
                raise ValueError(
                    "Elija la fila (o la columna) de la que sale el valor: la "
                    "procedencia que se registra la nombra, y sin ella la "
                    "memoria no puede decir de donde vino el numero.")
            return dec.declarar_desde_tabla(
                self.clave, valor,
                tabla_id=self.ventana.tabla.tabla_id,
                filas=(fila,) if fila else (),
                columnas=(columna,) if columna else ())
        if cara is vn.Cara.RANGO:
            return dec.declarar_en_rango(self.clave, valor)
        return dec.declarar_valor(self.clave, valor)

    # ------------------------------------------------------------------
    # Utilidades de pintado
    # ------------------------------------------------------------------
    def _parrafo(self, p, texto, negrita=False):
        fuente = FUENTE_NEGRITA if negrita else FUENTE_CUERPO
        ttk.Label(p, text=texto, wraplength=980, justify="left",
                  font=fuente).pack(anchor="w", pady=2)

    def _aviso(self, p, titulo, texto, color):
        marco = ttk.Frame(p, padding=6)
        marco.pack(fill="x", pady=4)
        ttk.Label(marco, text=titulo, foreground=color,
                  font=FUENTE_NEGRITA).pack(anchor="w")
        ttk.Label(marco, text=texto, wraplength=960, justify="left",
                  font=FUENTE_CUERPO).pack(anchor="w")


def abrir(master, clave, al_declarar=None) -> Optional[VentanaNormativa]:
    """
    Abre la ventana de una variable, o avisa si la clave no es una variable de
    entrada del expediente.

    El aviso sale por `messagebox` y no por excepcion porque el llamador es un
    doble clic en una tabla: un `KeyError` ahi seria una traza de Tk para lo
    que es una fila que todavia no esta censada.
    """
    try:
        return VentanaNormativa(master, clave, al_declarar=al_declarar)
    except KeyError as exc:
        messagebox.showinfo("Sin ventana normativa", str(exc))
        return None
