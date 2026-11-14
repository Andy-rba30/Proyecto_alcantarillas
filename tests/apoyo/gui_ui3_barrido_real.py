"""
tests/apoyo/gui_ui3_barrido_real.py
===================================
UI-3 SOBRE LA VENTANA DE VERDAD: el boton «Barrido…» de la pestaña 2 (ficha
PF-3-01, cerrada por UI-3; la decision de donde corre, en la ficha UI3-01).

    python -m tests.apoyo.gui_ui3_barrido_real <directorio de salida>

Corre en un proceso limpio por la misma razon que `gui_ui1_hidrologia_real.py`:
`test_gui_contrato.py` instala dobles de `tkinter` y con ellos la ventana
seria un espejismo. Las entradas son las de la GUIA DE PERFIL
(`docs/guia_perfil.md`), escritas por el mismo `Taller` con que
`tests/test_guia_perfil.py` la ejecuta: DATOS DE PRUEBA.

Que se mide, en orden:

  1. el boton, criterio a criterio: encendido con ventana, apagado con su
     motivo sin ella, derivado, y con una ventana de barrido ya abierta;
  2. un valor fuera de la ventana (`HW_D_max` = 9.9): el editor no lo deja
     añadir y, metido a mano en la lista, la puerta del Toplevel lo rechaza
     sin lanzar ningun hijo y sin mover el estado declarado;
  3. el barrido de la guia (`n_celdas_cajon` = 1, 2) en un proceso hijo,
     con la ventana respondiendo mientras corre; sus lineas contra las que
     la CLI imprime para la MISMA sesion (la que la ventana le paso al hijo);
     «Guardar JSON del barrido»;
  4. un segundo barrido cancelado;
  5. al cerrar: la pestaña 2 se refresca, el boton vuelve, y el estado
     declarado, los [S], el informe vigente, su volcado, los exportadores y
     las filas de la pestaña 2 son los de antes;
  6. cerrar la ventana PRINCIPAL con un barrido en marcha no deja el hijo
     huerfano ni su carpeta en el temporal (revision de UI-3, H3).

Y desde la revision de UI-3 la ventana pisa ademas `espesor_pared_conducto`
con el valor del archivo (claves enteras, H2), y la corrida del primer valor
del barrido tiene que ser la de la ventana (H7): eso prueba que la sesion del
hijo ES el estado de la ventana, y no solo que la tabla se pinta bien.
"""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

import cli                                             # noqa: E402
from src import criterios_adoptados as ca             # noqa: E402
from src import declaracion as dec                     # noqa: E402
from src import sesion as ses                          # noqa: E402

CLAVE_DE_LA_GUIA = "n_celdas_cajon"
CLAVE_CON_RANGO = "HW_D_max"
CLAVE_SIN_VENTANA = "TR_evento_extremo"
CLAVE_DERIVADA = "coeficiente_escorrentia_superficie_vial"
CLAVE_DE_CLAVES_ENTERAS = "espesor_pared_conducto"
DENTRO, FUERA = 1.3, 9.9
TOPE_S = 600


def _boton(ventana):
    return {"encendido": str(ventana.btn_barrido.cget("state")) == "normal",
            "motivo": ventana.btn_barrido.motivo}


def _seleccionar(ventana, raiz, clave):
    ventana.filtro_texto_var.set("")
    raiz.update()
    ventana.tree_criterios_todos.selection_set(clave)
    ventana.tree_criterios_todos.see(clave)
    raiz.update()


def _exportadores(ventana):
    """Todo el grupo de la pestaña 4 (`BOTONES_DE_EXPORTACION`, UI-2), no una copia."""
    import gui.app as gapp
    return {nombre: {"encendido": str(getattr(ventana, nombre).cget("state")) == "normal",
                     "motivo": getattr(ventana, nombre).motivo}
            for nombre in gapp.BOTONES_DE_EXPORTACION}


def _filas_de_la_pestana_2(ventana):
    arbol = ventana.tree_criterios_todos
    return [list(arbol.item(i, "values")) for i in arbol.get_children()]


def _sin_marca(datos):
    return ses.sin_marca_de_tiempo(json.loads(json.dumps(datos, ensure_ascii=False,
                                                         allow_nan=False)))


def _tabla_de_la_salida(stdout):
    lineas = stdout.splitlines()
    inicio = next(i for i, l in enumerate(lineas) if l.startswith("Barrido de '"))
    fin = next(i for i in range(inicio, len(lineas)) if not lineas[i].strip())
    return lineas[inicio:fin]


def _hasta_que_termine(vb, raiz, al_latir=None):
    latidos = 0
    limite = time.monotonic() + TOPE_S
    while vb.proceso is not None and not vb.proceso.estado.terminal:
        if time.monotonic() > limite:
            raise RuntimeError("el hijo del barrido no termino")
        raiz.update()
        latidos += 1
        if al_latir is not None:
            al_latir()
        time.sleep(0.05)
    raiz.update()
    return latidos


def _visible_en_la_pestana_2(ventana, raiz):
    """El boton cae dentro de la pestaña 2 en la geometria por defecto (1100x800)."""
    ventana.nb.select(ventana.tab_criterios)
    raiz.update()
    boton = ventana.btn_barrido.boton
    pestana = ventana.tab_criterios
    abajo_del_boton = boton.winfo_rooty() + boton.winfo_height()
    abajo_de_la_pestana = pestana.winfo_rooty() + pestana.winfo_height()
    return bool(boton.winfo_ismapped()) and abajo_del_boton <= abajo_de_la_pestana


def _toplevels(raiz):
    import tkinter as tk
    return [w for w in raiz.winfo_children() if isinstance(w, tk.Toplevel)]


def main(salida: Path) -> int:
    import ttkbootstrap as tb

    import gui.app as gapp
    from tests.test_guia_perfil import Taller

    salida.mkdir(parents=True, exist_ok=True)
    taller = Taller(salida / "taller")
    taller.preparar()
    guia = taller.raiz / "guia"
    dialogos = []
    gapp.messagebox.showinfo = lambda titulo, texto, *a, **k: dialogos.append(
        ("info", titulo, texto))
    gapp.messagebox.showerror = lambda titulo, texto, *a, **k: dialogos.append(
        ("error", titulo, texto))
    gapp.messagebox.askyesno = lambda *a, **k: True

    raiz = tb.Window(themename="litera")
    r = {}
    destruida = False
    try:
        ventana = gapp.ExpedienteApp(raiz)
        ventana.proyecto_var.set("Via de evitamiento")
        ventana.csv_var.set(str(guia / "puntos.csv"))
        ventana.datos_externos_var.set(str(guia / "externos.json"))
        ventana.datos_sitio_var.set(str(guia / "sitio.json"))
        ventana.externos_vars["luz_m"].set("2.75")
        ventana.alcance_var.set(cli.ALCANCE_PERFIL)
        raiz.update()
        # La declaracion de la guia (seccion 4), por «Aplicar» de la pestaña 2.
        _seleccionar(ventana, raiz, CLAVE_DE_LA_GUIA)
        ventana.valor_declarado_var.set("1")
        raiz.update()
        ventana._aplicar_valor_corrida()
        raiz.update()
        # Y `espesor_pared_conducto` PISADO con el MISMO valor del archivo, por
        # «Aplicar» con el literal que la pestaña 2 propone: un dict con el
        # diametro ENTERO de clave, que la sesion JSON escribe como texto
        # (revision de UI-3, H2).
        _seleccionar(ventana, raiz, CLAVE_DE_CLAVES_ENTERAS)
        archivo = ca.criterio(CLAVE_DE_CLAVES_ENTERAS).valor
        # Primero COPIADO DE UN JSON, con las claves enteras como texto: la
        # pestaña 2 lo rechaza en la puerta y no declara nada (N1).
        ventana.valor_declarado_var.set(repr(json.loads(json.dumps(archivo))))
        raiz.update()
        ventana._aplicar_valor_corrida()
        raiz.update()
        r["clave_de_texto"] = {
            "rotulo": ventana.lbl_estado_criterio.cget("text"),
            "declarado": CLAVE_DE_CLAVES_ENTERAS in ca.valores_dinamicos()}
        ventana.valor_declarado_var.set(repr(archivo))
        raiz.update()
        ventana._aplicar_valor_corrida()
        raiz.update()
        r["pisado"] = repr(ca.valores_dinamicos().get(CLAVE_DE_CLAVES_ENTERAS)) == repr(
            ca.criterio(CLAVE_DE_CLAVES_ENTERAS).valor)
        ventana.ejecutar_pipeline()
        raiz.update()
        informe = ventana.informe
        if informe is None:
            print("ERROR: la ventana no produjo informe:",
                  ventana.lbl_error_datos.cget("text"))
            return 1
        volcado_antes = _sin_marca(cli.informe_json(informe))
        estado_antes = dec.estado_de_sesion()
        sitio_antes = dec.estado_de_sitio_de_sesion()
        exportadores_antes = _exportadores(ventana)

        # 1. El boton, criterio a criterio.
        boton = {}
        for clave in (CLAVE_SIN_VENTANA, CLAVE_DERIVADA, CLAVE_CON_RANGO, CLAVE_DE_LA_GUIA):
            _seleccionar(ventana, raiz, clave)
            boton[clave] = _boton(ventana)
            if clave == CLAVE_SIN_VENTANA:
                r["visible_el_motivo"] = ventana.btn_barrido.tooltip.texto
        filas_antes = _filas_de_la_pestana_2(ventana)

        # 2. Fuera de la ventana.
        _seleccionar(ventana, raiz, CLAVE_CON_RANGO)
        ventana._abrir_barrido()
        raiz.update()
        vb = ventana.ventana_barrido
        boton["con_barrido_abierto"] = _boton(ventana)
        r["boton"] = boton
        vb.editor.poner_valor(FUERA)
        raiz.update()
        vb.anadir_valor()
        anadido = bool(vb.valores)
        vb.editor.poner_valor(DENTRO)
        raiz.update()
        vb.anadir_valor()
        valores_tras_anadir = list(vb.valores)
        vb.valores.append(FUERA)            # a mano: lo que el editor no deja
        vb._pintar_valores()
        vb.correr()
        raiz.update()
        r["fuera"] = {"anadido_por_el_editor": anadido,
                      "valores_tras_anadir": valores_tras_anadir,
                      "proceso_es_None": vb.proceso is None,
                      "estado": vb.lbl_estado.cget("text"),
                      "estado_de_sesion_igual": dec.estado_de_sesion() == estado_antes}
        vb.cerrar()
        raiz.update()

        # 3. El barrido de la guia.
        _seleccionar(ventana, raiz, CLAVE_DE_LA_GUIA)
        ventana._abrir_barrido()
        raiz.update()
        vb = ventana.ventana_barrido
        g = {"sin_fila_en_un_criterio_libre": not vb.esquema.opciones_de_tabla,
             "nota_presente": vb.nota_var is not None}
        for valor in (1, 2, 3):
            vb.editor.poner_valor(valor)
            raiz.update()
            vb.anadir_valor()
        # Quitar: el tercero, seleccionado en la lista de verdad.
        vb.lista_valores.selection_set("2")
        raiz.update()
        vb.quitar_valor()
        raiz.update()
        g["lista_tras_quitar"] = [list(vb.lista_valores.item(i, "values"))
                                  for i in vb.lista_valores.get_children()]
        vb.correr()
        g["pid_de_la_ventana"] = os.getpid()
        g["pid_del_hijo"] = (vb.proceso._proceso.pid
                             if vb.proceso is not None and vb.proceso._proceso else None)
        observado = {"informe": True, "estado": True}

        def _al_latir():
            observado["informe"] &= ventana.informe is informe
            observado["estado"] &= dec.estado_de_sesion() == estado_antes

        g["latidos_mientras_corria"] = _hasta_que_termine(vb, raiz, _al_latir)
        g["informe_igual_mientras_corria"] = observado["informe"]
        g["estado_igual_mientras_corria"] = observado["estado"]
        g["estado"] = vb.proceso.estado.value
        g["detalle"] = vb.proceso.detalle
        g["lineas_ventana"] = vb.txt_tabla.get("1.0", "end-1c").splitlines()
        g["boton_guardar_tras_terminar"] = str(vb.btn_guardar.cget("state")) == "normal"
        # La MISMA sesion que la ventana le paso al hijo, por la CLI.
        sesion_del_hijo = salida / "sesion_del_hijo.json"
        shutil.copyfile(vb.proceso.ruta_sesion, sesion_del_hijo)
        hecho = subprocess.run(
            [sys.executable, str(RAIZ / "cli.py"), "--sesion", str(sesion_del_hijo),
             "--barrido", "n_celdas_cajon=1,2", "--json", str(salida / "barrido_cli.json")],
            cwd=Path.cwd(), capture_output=True, text=True, timeout=TOPE_S)
        g["cli_codigo"] = hecho.returncode
        g["lineas_cli"] = _tabla_de_la_salida(hecho.stdout) if hecho.returncode == 0 else [
            hecho.stderr[-2000:]]
        guardado = salida / "barrido_guardado.json"
        gapp.filedialog.asksaveasfilename = lambda **kw: str(guardado)
        import gui.ventana_barrido as gvb
        gvb.filedialog.asksaveasfilename = lambda **kw: str(guardado)
        vb.guardar_json()
        g["json_guardado_igual_al_del_hijo"] = (
            guardado.is_file()
            and guardado.read_bytes() == vb.proceso.ruta_json.read_bytes())
        # LA SESION DEL HIJO ES EL ESTADO DE LA VENTANA (H7): la corrida del
        # primer valor --- el vigente, 1 --- es la corrida de la ventana.
        from src import comparador as compa
        primera = vb.proceso.resultado.corridas[0].informe_json
        lineas = compa.comparar(cli.informe_json(informe), primera).lineas()
        g["primera_igual_a_la_ventana"] = lineas[0].startswith("IGUALES")
        g["comparacion_con_la_ventana"] = lineas[:6]
        g["primera_dimensiona_todo"] = all(p["dimensionado"] for p in primera["puntos"])
        volcado_ventana = cli.informe_json(informe)
        g["origenes_iguales"] = (
            primera["expediente"]["corredor_del_proyecto"]["origen"]
            == volcado_ventana["expediente"]["corredor_del_proyecto"]["origen"]
            and [u["origen"] for u in primera["datos_sitio"]["usados"]]
            == [u["origen"] for u in volcado_ventana["datos_sitio"]["usados"]])
        r["guia"] = g

        # 4. Un segundo barrido, cancelado.
        vb.correr()
        vb.cancelar()
        _hasta_que_termine(vb, raiz)
        r["cancelado"] = {"estado": vb.proceso.estado.value,
                          "guardar_encendido": str(vb.btn_guardar.cget("state")) == "normal"}

        # 5. Al cerrar.
        refrescos = []
        original = ventana._llenar_tabla_criterios

        def _contar():
            refrescos.append(1)
            return original()

        ventana._llenar_tabla_criterios = _contar
        vb.cerrar()
        raiz.update()
        ventana._llenar_tabla_criterios = original
        r["visible_en_la_geometria_por_defecto"] = _visible_en_la_pestana_2(
            ventana, raiz)
        r["despues"] = {
            "refrescos_al_cerrar": len(refrescos),
            "ventana_barrido_es_None": ventana.ventana_barrido is None,
            "boton_encendido": _boton(ventana)["encendido"],
            "estado_de_sesion_igual": dec.estado_de_sesion() == estado_antes,
            "sitio_igual": dec.estado_de_sitio_de_sesion() == sitio_antes,
            "informe_es_el_mismo": ventana.informe is informe,
            "volcado_igual": _sin_marca(cli.informe_json(ventana.informe)) == volcado_antes,
            "exportadores_iguales": _exportadores(ventana) == exportadores_antes,
            "filas_de_la_pestana_2_iguales": _filas_de_la_pestana_2(ventana) == filas_antes,
            "toplevels_abiertos": len(_toplevels(raiz)),
            "dialogos_de_error": [d for d in dialogos if d[0] == "error"],
        }

        # 6. Cerrar la ventana PRINCIPAL con un barrido en marcha (H3): el hijo
        # termina y su carpeta de trabajo no queda en el temporal.
        _seleccionar(ventana, raiz, CLAVE_DE_LA_GUIA)
        ventana._abrir_barrido()
        raiz.update()
        vb = ventana.ventana_barrido
        for valor in (1, 2):
            vb.editor.poner_valor(valor)
            vb.anadir_valor()
        vb.correr()
        proceso = vb.proceso
        en_marcha = proceso is not None and not proceso.estado.terminal
        raiz.destroy()
        destruida = True
        r["cerrar_la_principal"] = {
            "en_marcha_al_cerrar": en_marcha,
            "hijo_terminado": proceso._proceso.poll() is not None,
            "carpeta_retirada": not proceso.directorio_trabajo.exists(),
        }
    finally:
        if not destruida:
            raiz.destroy()

    (salida / "resumen_ui3.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in r.items() if k != "guia"}, ensure_ascii=False)[:4000])
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[3])
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
