# -*- coding: utf-8 -*-
"""
gui/ventana_barrido.py
======================
LA VENTANA DEL BARRIDO DE SENSIBILIDAD de la pestaña 2 (UI-3, ficha PF-3-01;
la decision de donde corre, en la ficha UI3-01).

El boton «Barrido…» de la pestaña 2 abre esta ventana sobre el criterio
seleccionado, si tiene ventana de sensibilidad. Aqui se pide la LISTA de
valores con el editor tipado de E-B del criterio (`gui/editores.py`, el
mismo que la pestaña 2 monta, sin su campo de nota), un valor por fila, y la
fila y la nota que valen para TODOS los valores --- las de `--barrido-fila`
y `--barrido-nota` de la CLI ---. Se corre, se pinta la tabla y se guarda
su JSON. Nada mas.

Lo que esta ventana NO hace, y por que
--------------------------------------
* NO DECIDE NINGUNA REGLA. La puerta es `barrido.verificar_valores`, la de
  la CLI, que declara cada valor por `editores.declarar` --- la puerta de
  «Aplicar»: forma, ventana, fila o nota de un criterio de tabla,
  trazabilidad de un ensayo --- y deshace. Se cierra ANTES de lanzar nada:
  un valor fuera de la ventana se dice aqui y no corre ninguna corrida.
* NO CORRE EL PIPELINE EN ESTE PROCESO. El barrido corre en un proceso
  hijo, la propia CLI con la sesion de la ventana
  (`gui/proceso_barrido.py`), y se sondea con `after`: la ventana no se
  congela, y el estado declarado de la pestaña 2 y el informe de las
  pestañas 3 y 4 no se tocan mientras corre ni despues. La unica huella en
  este proceso es la de la puerta, que declara y repone dentro del mismo
  gesto (`restaurar_sesion(sustituir=True)`).
* NO ESCRIBE OTRAS LINEAS. La tabla es `barrido.lineas_de_la_tabla` sobre
  el JSON del hijo (`barrido.resultado_del_volcado`): las mismas lineas que
  la CLI imprime, en monoespaciada y sin tocar una palabra.
* NO ARMA MEMORIA NI EXPORTA EL EXPEDIENTE. El barrido es un anexo de la
  tesis; lo que se guarda es su JSON (`{"barridos": [...]}`), el mismo que
  escribe `cli.py --barrido --json`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import tkinter as tk
from tkinter import filedialog, ttk

from src import barrido as _barrido
from src import criterios_adoptados as ca
from src import editores as sed
from gui import componentes as comp
from gui import editores as ged
from gui.componentes import (COLOR_AVISO, COLOR_ERROR, COLOR_OK, BotonAccion,
                             MarcoScroll, Panel, Tooltip,
                             interpretar_texto_declarado)
from gui.proceso_barrido import EstadoDelBarrido, ProcesoBarrido

# Cada cuanto se sondea el proceso hijo, en ms. Cadencia de interfaz, no un
# valor del expediente (la misma que el sondeo del PDF de EXT-8).
CADENCIA_SONDEO_BARRIDO_MS = 250   # literal-ok: cadencia del sondeo del subproceso, ms

# La opcion «sin fila» del desplegable de la procedencia: cada valor entra
# entonces con su nota, o nombrando su propia fila (el texto que es la
# clave de una fila la nombra, `editores.fila_implicita`).
FILA_NINGUNA = "(ninguna: cada valor con la nota, o nombrando su propia fila)"

# Los motivos, como DATO (la regla de `gui/app.py`): un boton apagado o un
# rechazo dicen por que con el mismo texto cada vez.
MOTIVO_SIN_VALORES = "añada al menos un valor a la lista antes de correr el barrido"
MOTIVO_SIN_CSV = ("la pestaña 1 no tiene CSV de puntos criticos: el barrido corre "
                  "sobre el mismo expediente que EJECUTAR")
MOTIVO_BARRIDO_EN_MARCHA = "el barrido esta corriendo en un proceso aparte"
MOTIVO_SIN_BARRIDO_EN_MARCHA = "no hay ningun barrido en marcha"
MOTIVO_SIN_RESULTADO = "todavia no hay un barrido terminado cuyo JSON guardar"
MOTIVO_SIN_SELECCION = "seleccione un valor de la lista para quitarlo"
PREFIJO_RECHAZO = "No se corrio ninguna corrida: "

AVISO_DEL_BARRIDO = (
    "Corre el calculo una vez por valor en un PROCESO APARTE, sobre el estado "
    "de la ventana al pulsar «Correr el barrido»: las entradas de la pestaña 1 "
    "y lo declarado en la pestaña 2. No toca el informe de las pestañas 3 y 4 "
    "ni lo declarado, y no arma memoria: es un anexo de la tesis. El primer "
    "valor de la lista es la referencia contra la que se compara cada corrida.")
AYUDA_DE_LOS_VALORES = (
    "Componga cada valor con el editor y pulse «Añadir valor». Elegir una fila "
    "en el editor solo PROPONE su valor: la procedencia del barrido se elige "
    "abajo y vale para todos los valores (como --barrido-fila y --barrido-nota "
    "de la linea de comandos).")


def texto_de_la_ventana(sensibilidad: Any) -> str:
    """La ventana de la ficha, para leerla: los textos de una tupla, separados."""
    if isinstance(sensibilidad, (tuple, list)) and all(isinstance(x, str)
                                                       for x in sensibilidad):
        return " · ".join(sensibilidad)
    return repr(sensibilidad)


class VentanaBarrido:
    """
    El Toplevel del barrido de UNA clave. `sesion_de_la_ventana` devuelve la
    sesion que el hijo repone, leida AL PULSAR «Correr» (la ventana pudo
    cambiar desde que se abrio esta); `al_cerrar` es el gesto de la pestaña
    2 al volver (refrescarse).
    """

    def __init__(self, master, clave: str, *,
                 sesion_de_la_ventana: Callable[[], Dict[str, Any]],
                 al_cerrar: Callable[[], None], color_neutro: str):
        self.master = master
        self.clave = clave
        self.esquema = sed.esquema_de(clave)
        self.sesion_de_la_ventana = sesion_de_la_ventana
        self.al_cerrar = al_cerrar
        self.color_neutro = color_neutro
        self.valores: List[Any] = []
        self.proceso: Optional[ProcesoBarrido] = None
        self.editor = None
        self.literal_var = None
        self._sondeo = None
        self._cerrada = False
        self.top = tk.Toplevel(master, background=comp.SUPERFICIE)
        self.top.title(f"Barrido de sensibilidad: {clave}")
        self.top.geometry("1040x780")
        self.top.transient(master)
        self.top.bind("<Escape>", lambda _evt: self.cerrar())
        self.top.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.top.bind("<Destroy>", self._al_destruirse, add="+")
        self._construir()
        self._refrescar_botones()

    # ------------------------------------------------------------------
    # Construccion
    # ------------------------------------------------------------------
    def _construir(self):
        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(1, weight=1)
        c = self.esquema
        cabecera = ttk.Frame(self.top, padding=(12, 10, 12, 4))
        cabecera.grid(row=0, column=0, sticky="ew")
        ficha = ca.criterio(self.clave)     # la ficha, solo para leerla
        ttk.Label(cabecera, text=f"Barrido de «{self.clave}» [{ficha.etiqueta}]",
                  style="Header.TLabel").pack(anchor="w")
        ttk.Label(cabecera, text=ficha.concepto, wraplength=980, justify="left",
                  style="Ayuda.TLabel").pack(anchor="w")
        ttk.Label(cabecera, text="Ventana (ficha): "
                  + texto_de_la_ventana(ficha.sensibilidad),
                  wraplength=980, justify="left").pack(anchor="w", pady=(4, 0))
        ttk.Label(cabecera, text=AVISO_DEL_BARRIDO, wraplength=980, justify="left",
                  style="Ayuda.TLabel").pack(anchor="w", pady=(4, 0))

        # Arriba, con scroll, lo que se teclea (valores y procedencia);
        # abajo la tabla. Las ACCIONES van fuera de los dos, en su propia
        # fila al pie: con el editor de un dict el formulario no cabe, y un
        # «Correr» que hay que buscar desplazando es un boton escondido.
        partes = ttk.PanedWindow(self.top, orient="vertical")
        partes.grid(row=1, column=0, sticky="nsew", padx=12, pady=(4, 4))
        arriba = MarcoScroll(partes)
        abajo = ttk.Frame(partes)
        # Tres quintos para lo que se teclea y dos para la tabla, colocados
        # al mostrarse (`repartir_al_mostrar`); despues el divisor es del
        # usuario.
        partes.add(arriba, weight=3)
        partes.add(abajo, weight=2)
        comp.repartir_al_mostrar(partes)
        self._construir_valores(arriba.interior, c)
        self._construir_procedencia(arriba.interior, c)
        self._construir_tabla(abajo)
        pie = ttk.Frame(self.top, padding=(12, 4, 12, 10))
        pie.grid(row=2, column=0, sticky="ew")
        self._construir_acciones(pie)

    def _construir_valores(self, p, c):
        panel = Panel(p, "Valores a barrer (un valor por fila)")
        panel.pack(fill="x", pady=(0, 8))
        f = panel.interior
        ttk.Label(f, text=AYUDA_DE_LOS_VALORES, wraplength=940, justify="left",
                  style="Ayuda.TLabel").pack(anchor="w", pady=(0, 4))
        f_editor = ttk.Frame(f)
        f_editor.pack(fill="x")
        self.editor = ged.construir_editor(
            f_editor, self.clave, color_neutro=self.color_neutro,
            al_cambiar=lambda: None, con_nota=False)
        self.editor.marco.pack(fill="x")
        try:
            self.editor.poner_valor(c.valor_actual)
        except ValueError:
            pass        # el valor vigente no cabe en los campos: se teclea
        if c.tipo_de_editor == sed.LITERAL:
            self.literal_var = tk.StringVar(
                value="" if c.valor_actual is None else repr(c.valor_actual))
            # El rotulo que el editor sin campos nombra («Valor nuevo»).
            ttk.Label(f, text="Valor nuevo:").pack(anchor="w", pady=(4, 0))
            ent = ttk.Entry(f, textvariable=self.literal_var)
            ent.pack(fill="x", pady=(4, 0))
            Tooltip(ent, "El valor ENTERO, como literal: el mismo parser que el\n"
                         "campo «Valor nuevo» de la pestaña 2.")
        f_botones = ttk.Frame(f)
        f_botones.pack(fill="x", pady=(6, 4))
        self.btn_anadir = BotonAccion(
            f_botones, "Añadir valor", fondo=comp.AZUL,
            activebackground=comp.AZUL_OSCURO, activeforeground="white",
            command=self.anadir_valor,
            ayuda="Añade al final de la lista el valor que el editor compone.\n"
                  "Si un campo del editor no arma (fuera de su ventana, vacio),\n"
                  "no se añade nada y se dice por que.")
        self.btn_anadir.pack(side="left", ipadx=6, ipady=2)
        self.btn_quitar = BotonAccion(
            f_botones, "Quitar valor", letra=BotonAccion.DISCRETA,
            command=self.quitar_valor,
            ayuda="Quita de la lista el valor seleccionado.")
        self.btn_quitar.pack(side="left", padx=(8, 0), ipadx=6, ipady=2)
        self.lista_valores = ttk.Treeview(f, columns=("n", "valor"), show="headings",
                                          height=4)
        self.lista_valores.heading("n", text="#")
        self.lista_valores.heading("valor", text="Valor (el primero es la referencia)")
        self.lista_valores.column("n", width=40, anchor="center")
        self.lista_valores.column("valor", width=820, anchor="w")
        self.lista_valores.pack(fill="x")

    def _construir_procedencia(self, p, c):
        panel = Panel(p, "Procedencia de los valores (vale para todos)")
        panel.pack(fill="x", pady=(0, 8))
        f = panel.interior
        self.fila_var = tk.StringVar(value=FILA_NINGUNA)
        if c.opciones_de_tabla and c.tipo_de_editor != sed.SERIE_DE_CLAVES:
            ttk.Label(f, text=f"Fila de {c.tabla_id} de la que provienen:").pack(anchor="w")
            cmb = ttk.Combobox(
                f, textvariable=self.fila_var, state="readonly", width=110,
                values=[FILA_NINGUNA] + [ged.rotulo_de_opcion(o)
                                         for o in c.opciones_de_tabla])
            cmb.pack(fill="x", pady=(2, 6))
            Tooltip(cmb, "La fila que la procedencia de CADA valor cita\n"
                         "(--barrido-fila). Un valor que difiere de su celda\n"
                         "exige la nota, como en «Aplicar».")
        ttk.Label(f, text=ged.rotulo_de_la_nota(c), wraplength=940,
                  justify="left").pack(anchor="w")
        self.nota_var = tk.StringVar()
        ent = ttk.Entry(f, textvariable=self.nota_var)
        ent.pack(fill="x", pady=(2, 0))
        Tooltip(ent, "Viaja con la procedencia de cada valor (--barrido-nota).")

    def _construir_acciones(self, p):
        f = ttk.Frame(p)
        f.pack(fill="x", pady=(0, 4))
        self.btn_correr = BotonAccion(
            f, "Correr el barrido", letra=BotonAccion.GRANDE, fondo=comp.AZUL,
            activebackground=comp.AZUL_OSCURO, activeforeground="white",
            command=self.correr,
            ayuda="Cierra la puerta de TODOS los valores (la de «Aplicar»)\n"
                  "y, si pasan, corre el barrido en un proceso aparte.")
        self.btn_correr.pack(side="left", ipadx=8, ipady=3)
        self.btn_cancelar = BotonAccion(
            f, "Cancelar el barrido", letra=BotonAccion.DISCRETA,
            command=self.cancelar, motivo=MOTIVO_SIN_BARRIDO_EN_MARCHA,
            ayuda="Termina el proceso del barrido; no deja tabla.")
        self.btn_cancelar.pack(side="left", padx=(8, 0), ipadx=6, ipady=3)
        self.btn_guardar = BotonAccion(
            f, "Guardar JSON del barrido...", fondo=comp.TEXTO_SUAVE,
            command=self.guardar_json, motivo=MOTIVO_SIN_RESULTADO,
            ayuda="Guarda el JSON del barrido tal como lo escribe\n"
                  "`cli.py --barrido --json`: las corridas con su volcado\n"
                  "entero y la tabla por punto.")
        self.btn_guardar.pack(side="left", padx=(8, 0), ipadx=6, ipady=3)
        ttk.Button(f, text="Cerrar", command=self.cerrar).pack(side="right")
        self.lbl_estado = ttk.Label(p, text="", wraplength=960, justify="left",
                                    style="Ayuda.TLabel")
        self.lbl_estado.pack(anchor="w", pady=(4, 0))

    def _construir_tabla(self, p):
        panel = Panel(p, "Tabla del barrido (las mismas lineas que la linea de comandos)")
        panel.pack(fill="both", expand=True)
        f = panel.interior
        f.columnconfigure(0, weight=1)
        f.rowconfigure(0, weight=1)
        self.txt_tabla = comp.texto_plano(f, wrap="none", height=12)
        self.txt_tabla.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(f, orient="vertical", command=self.txt_tabla.yview)
        horizontal = ttk.Scrollbar(f, orient="horizontal", command=self.txt_tabla.xview)
        self.txt_tabla.configure(yscrollcommand=vertical.set,
                                 xscrollcommand=horizontal.set, state="disabled")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

    # ------------------------------------------------------------------
    # La lista de valores
    # ------------------------------------------------------------------
    def valor_del_editor(self) -> Any:
        """El valor que el editor compone (o el literal, para el editor sin campos)."""
        if self.esquema.tipo_de_editor == sed.LITERAL:
            return interpretar_texto_declarado(self.literal_var.get())
        return self.editor.valor()

    def anadir_valor(self):
        try:
            valor = self.valor_del_editor()
        except ValueError as exc:
            self._decir(f"No se añadio: {exc}", COLOR_ERROR)
            return
        self.valores.append(valor)
        self._pintar_valores()
        self._decir(f"Valor {valor!r} añadido: la lista tiene {len(self.valores)}.",
                    COLOR_OK)

    def quitar_valor(self):
        seleccion = self.lista_valores.selection()
        if not seleccion:
            self._decir(MOTIVO_SIN_SELECCION, COLOR_AVISO)
            return
        valor = self.valores.pop(int(seleccion[0]))
        self._pintar_valores()
        self._decir(f"Valor {valor!r} quitado de la lista.", COLOR_AVISO)

    def _pintar_valores(self):
        for item in self.lista_valores.get_children():
            self.lista_valores.delete(item)
        for indice, valor in enumerate(self.valores):
            self.lista_valores.insert("", "end", iid=str(indice),
                                      values=(indice + 1, repr(valor)))

    def _fila(self) -> str:
        """La clave de la fila elegida para la procedencia, o '' (ninguna)."""
        rotulo = self.fila_var.get()
        if not rotulo or rotulo == FILA_NINGUNA:
            return ""
        opcion = ged.opcion_del_rotulo(self.esquema, rotulo)
        return "" if opcion is None else opcion.fila

    # ------------------------------------------------------------------
    # Correr, sondear, cancelar
    # ------------------------------------------------------------------
    def correr(self):
        """
        LA PUERTA Y DESPUES EL HIJO. `barrido.verificar_valores` --- la de la
        CLI, con la fila y la nota de «Aplicar» --- sobre todos los valores;
        si alguno no pasa, se dice aqui y no se lanza nada. La sesion se lee
        AHORA, no al abrir esta ventana.
        """
        if self.proceso is not None and not self.proceso.estado.terminal:
            return
        if not self.valores:
            self._decir(MOTIVO_SIN_VALORES, COLOR_ERROR)
            return
        sesion = self.sesion_de_la_ventana()
        if not str(sesion.get("csv") or "").strip():
            self._decir(MOTIVO_SIN_CSV, COLOR_ERROR)
            return
        fila, nota = self._fila(), self.nota_var.get().strip()
        valores = tuple(self.valores)
        try:
            _barrido.verificar_valores(self.clave, valores, fila=fila, nota=nota)
        except (ValueError, KeyError) as exc:
            self._decir(f"{PREFIJO_RECHAZO}{exc}", COLOR_ERROR)
            return
        proceso = ProcesoBarrido(sesion=sesion, clave=self.clave, valores=valores,
                                 fila=fila, nota=nota)
        proceso.iniciar()
        if proceso.estado.terminal:
            # No arranco: se dice, no queda nada «en marcha», y el barrido
            # ANTERIOR sigue entero --- su tabla y su JSON guardable ---,
            # porque solo se suelta cuando el nuevo arranca (revision de
            # UI-3, H4: soltarlo antes dejaba su tabla pintada y «Guardar»
            # encendido sin nada que guardar).
            proceso.limpiar()
            anterior = (" La tabla de abajo es la del barrido anterior."
                        if self.proceso is not None
                        and self.proceso.estado is EstadoDelBarrido.TERMINADO else "")
            self._decir(proceso.detalle + anterior, COLOR_ERROR)
            self._refrescar_botones()
            return
        self._soltar_proceso()
        self.proceso = proceso
        self._pintar_tabla(())
        self._decir(f"Barrido de '{self.clave}' sobre {len(valores)} valor(es) en "
                    "marcha en un proceso aparte.", COLOR_AVISO)
        self._refrescar_botones()
        self._sondeo = self.top.after(CADENCIA_SONDEO_BARRIDO_MS, self._sondear)

    def _sondear(self):
        """Un latido del `after`: pregunta al hijo y se reprograma."""
        self._sondeo = None
        proceso = self.proceso
        if proceso is None or self._cerrada:
            return
        if not proceso.sondear().terminal:
            self._decir(f"Barrido en marcha ({proceso.segundos():.0f} s) en un "
                        "proceso aparte.", COLOR_AVISO)
            self._sondeo = self.top.after(CADENCIA_SONDEO_BARRIDO_MS, self._sondear)
            return
        self._terminar(proceso)

    def _terminar(self, proceso):
        """El estado terminal, a la vista: la tabla, o el motivo."""
        if proceso.estado is EstadoDelBarrido.TERMINADO:
            self._pintar_tabla(proceso.lineas)
            self._decir(proceso.detalle, COLOR_OK)
        elif proceso.estado is EstadoDelBarrido.CANCELADO:
            self._decir(proceso.detalle, COLOR_AVISO)
        else:
            self._pintar_tabla(proceso.detalle.splitlines())
            self._decir("El barrido fallo: lo que dijo el proceso esta abajo.",
                        COLOR_ERROR)
        self._refrescar_botones()

    def cancelar(self):
        if self.proceso is not None and not self.proceso.estado.terminal:
            self.proceso.cancelar()
            self._decir("Cancelando el barrido...", COLOR_AVISO)

    def guardar_json(self, ruta=None):
        """El JSON del hijo, tal cual (el de `cli.py --barrido --json`)."""
        if self.proceso is None or self.proceso.estado is not EstadoDelBarrido.TERMINADO:
            self._decir(MOTIVO_SIN_RESULTADO, COLOR_AVISO)
            return None
        if ruta is None:
            ruta = filedialog.asksaveasfilename(
                title="Guardar JSON del barrido", defaultextension=".json",
                filetypes=[("Archivo JSON", "*.json")],
                initialfile=f"barrido_{self.clave}.json", parent=self.top)
        if not ruta:
            return None
        try:
            destino = self.proceso.copiar_json(Path(ruta))
        except OSError as exc:
            self._decir(f"No se pudo guardar el JSON del barrido: {exc}", COLOR_ERROR)
            return None
        self._decir(f"JSON del barrido guardado: {destino}", COLOR_OK)
        return destino

    def cerrar(self):
        """
        Cierra la ventana: termina el hijo si sigue en marcha y retira su
        directorio (`_soltar_todo`), y la pestaña 2 se refresca
        (`al_cerrar`).
        """
        if self._cerrada:
            return
        self._soltar_todo()
        if self.editor is not None:
            self.editor.desmontar()
            self.editor = None
        self.top.destroy()
        self.al_cerrar()

    def _al_destruirse(self, evento):
        """
        La ventana se destruye SIN pasar por `cerrar`: la principal se cerro
        (`raiz.destroy()` destruye sus Toplevel) o alguien la destruyo a
        mano. Hasta la revision de UI-3 (H3) un hijo en marcha quedaba
        huerfano y su carpeta en el temporal para siempre, porque la
        limpieza se reprogramaba con `after` sobre una ventana que ya no
        existia. El `<Destroy>` del Toplevel llega tambien por cada hijo
        suyo: solo cuenta el del propio Toplevel.
        """
        if evento.widget is not self.top or self._cerrada:
            return
        self._soltar_todo()
        try:
            self.al_cerrar()
        except tk.TclError:
            pass        # la ventana principal tambien se esta destruyendo

    def _soltar_todo(self):
        """Ningun sondeo pendiente, ningun hijo vivo, ningun directorio de trabajo."""
        self._cerrada = True
        if self._sondeo is not None:
            try:
                self.top.after_cancel(self._sondeo)
            except tk.TclError:
                pass
            self._sondeo = None
        if self.proceso is not None:
            self.proceso.terminar_y_limpiar()

    # ------------------------------------------------------------------
    # Pintar
    # ------------------------------------------------------------------
    def _soltar_proceso(self):
        """El barrido anterior, si termino, deja su directorio de trabajo."""
        if self.proceso is not None and self.proceso.estado.terminal:
            self.proceso.limpiar()
            self.proceso = None

    def _refrescar_botones(self):
        en_marcha = self.proceso is not None and not self.proceso.estado.terminal
        terminado = (self.proceso is not None
                     and self.proceso.estado is EstadoDelBarrido.TERMINADO)
        self.btn_correr.estado(not en_marcha, MOTIVO_BARRIDO_EN_MARCHA)
        self.btn_anadir.estado(not en_marcha, MOTIVO_BARRIDO_EN_MARCHA)
        self.btn_quitar.estado(not en_marcha, MOTIVO_BARRIDO_EN_MARCHA)
        self.btn_cancelar.estado(en_marcha, MOTIVO_SIN_BARRIDO_EN_MARCHA)
        self.btn_guardar.estado(terminado, MOTIVO_SIN_RESULTADO)

    def _pintar_tabla(self, lineas):
        """Las lineas tal cual, sin una palabra distinta de la CLI."""
        self.txt_tabla.configure(state="normal")
        self.txt_tabla.delete("1.0", "end")
        self.txt_tabla.insert("1.0", "\n".join(lineas))
        self.txt_tabla.configure(state="disabled")

    def _decir(self, texto, color=None):
        self.lbl_estado.config(text=texto, foreground=color or "")
