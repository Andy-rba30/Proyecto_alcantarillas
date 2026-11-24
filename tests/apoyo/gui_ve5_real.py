"""
tests/apoyo/gui_ve5_real.py
===========================
VE-5 (lote «gui») SOBRE LA VENTANA DE VERDAD: lo que solo se ve con Tk y
una pantalla (`tests/test_ve5_gui_ventana.py` lo juzga).

    python -m tests.apoyo.gui_ve5_real <directorio de salida>

Corre en un proceso limpio por la misma razon que `gui_ui5_real.py`:
`test_gui_contrato.py` instala dobles de `tkinter`.

Que se mide, en orden:

  1. (item 38, ficha UI4-01) a 900 x 620 --- el `minsize` de la ventana ---
     los siete exportadores de la pestaña 4, mapeados, enteros y dentro del
     area visible; y con la letra de los botones agrandada (otra escala de
     pantalla), lo mismo, porque las filas se parten solas;
  2. (item 38, ficha UI3-01) a la misma geometria, con un criterio de tabla
     seleccionado en la pestaña 2, la columna derecha pide mas alto que la
     vista y desplazandola se llega a los cinco botones del panel;
  3. (item 40, ficha T6-04) los tres campos nuevos de la pestaña 1 existen,
     viajan en «Guardar sesion» y una sesion de formato 3 sin ellos los deja
     vacios;
  4. (item 49, ficha UI5-01 a) tras una corrida, escribir en el JSON de
     datos de sitio, en un dato que no esta en el CSV o en el alcance retira
     el informe con `MOTIVO_ENTRADA_CAMBIADA`.

DATOS DE PRUEBA: el CSV de perfil de ejemplo.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

GEOMETRIA_MINIMA = "900x620"
CRITERIO_DE_TABLA = "n_manning_cajon"
BOTONES_DEL_PANEL = ("btn_aplicar_corrida", "btn_quitar_declarado",
                     "btn_barrido", "btn_ventana_norma", "btn_guardar_archivo")
CAMPOS_NUEVOS = ("S_conducto", "bombeo", "peralte")
CSV_PERFIL = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"


def _caben(ventana, raiz):
    import gui.app as gapp
    ventana.nb.select(ventana.tab_resumen)
    raiz.update()
    lienzo = ventana.tab_resumen.canvas
    derecha = lienzo.winfo_rootx() + lienzo.winfo_width()
    salida = {}
    for nombre in gapp.BOTONES_DE_EXPORTACION:
        boton = getattr(ventana, nombre).boton
        salida[nombre] = {
            "mapeado": bool(boton.winfo_ismapped()),
            "entero": boton.winfo_width() >= boton.winfo_reqwidth(),
            "dentro": boton.winfo_rootx() + boton.winfo_width() <= derecha}
    return salida


def _entrada_de(raiz, variable):
    pendientes = [raiz]
    while pendientes:
        w = pendientes.pop()
        pendientes.extend(w.winfo_children())
        try:
            if str(w.cget("textvariable")) == str(variable):
                return w
        except Exception:                       # widget sin esa opcion
            continue
    return None


def main(salida: Path) -> int:
    import tkinter.font as tkfont

    import ttkbootstrap as tb

    import gui.app as gapp

    salida.mkdir(parents=True, exist_ok=True)
    dialogos = []
    gapp.messagebox.showinfo = lambda *a, **k: dialogos.append(("info",) + a)
    gapp.messagebox.showerror = lambda *a, **k: dialogos.append(("error",) + a)
    raiz = tb.Window(themename="litera")
    r = {}
    try:
        ventana = gapp.ExpedienteApp(raiz)
        raiz.geometry(GEOMETRIA_MINIMA)
        raiz.update()
        r["geometria"] = [raiz.winfo_width(), raiz.winfo_height()]
        r["minsize"] = list(raiz.minsize())

        # 1. Los exportadores a 900 px, y con la letra agrandada.
        r["exportadores_900"] = _caben(ventana, raiz)
        r["filas_900"] = [list(map(list, f.disposicion()))
                          for f in ventana.filas_de_exportacion]
        grande = tkfont.Font(family=tkfont.nametofont("TkDefaultFont").actual("family"),
                             size=18, weight="bold")
        for nombre in gapp.BOTONES_DE_EXPORTACION:
            getattr(ventana, nombre).boton.configure(font=grande)
        raiz.update()
        r["exportadores_letra_grande"] = _caben(ventana, raiz)
        r["filas_letra_grande"] = [list(map(list, f.disposicion()))
                                   for f in ventana.filas_de_exportacion]

        # 2. La columna derecha de la pestaña 2, con un criterio de tabla.
        ventana.nb.select(ventana.tab_criterios)
        raiz.update()
        tabla = ventana.tree_criterios_todos
        ventana.filtro_texto_var.set(CRITERIO_DE_TABLA)
        raiz.update()
        tabla.selection_set(CRITERIO_DE_TABLA)
        tabla.see(CRITERIO_DE_TABLA)
        raiz.update()
        lienzo = ventana.columna_declarar.canvas
        arriba = lienzo.winfo_rooty()
        abajo = arriba + lienzo.winfo_height()
        region = [int(float(x)) for x in str(lienzo.cget("scrollregion")).split()]
        r["columna"] = {"seleccionado": ventana._clave_criterio_seleccionado,
                        "alto_vista": lienzo.winfo_height(),
                        "alto_contenido": region[3] - region[1] if region else 0}

        def visibles():
            raiz.update()
            return {n: (bool(getattr(ventana, n).boton.winfo_ismapped())
                        and getattr(ventana, n).boton.winfo_rooty() >= arriba
                        and getattr(ventana, n).boton.winfo_rooty()
                        + getattr(ventana, n).boton.winfo_height() <= abajo)
                    for n in BOTONES_DEL_PANEL}

        lienzo.yview_moveto(0.0)
        r["columna"]["visibles_arriba"] = visibles()
        lienzo.yview_moveto(1.0)
        r["columna"]["visibles_abajo"] = visibles()

        # 3. Los tres campos nuevos de la pestaña 1, y la sesion.
        r["campos"] = {c: _entrada_de(raiz, ventana.externos_vars[c]) is not None
                       for c in CAMPOS_NUEVOS}
        ventana.externos_vars["S_conducto"].set("0,004")
        ventana.externos_vars["peralte"].set("-0,02")
        r["banderas"] = {c: ventana._leer_banderas()[c] for c in CAMPOS_NUEVOS}
        r["sesion_externos"] = {c: ventana._datos_de_sesion()["externos"][c]
                                for c in CAMPOS_NUEVOS}
        vieja = salida / "sesion_v3.json"
        vieja.write_text(json.dumps({
            "formato_version": 3, "app_version": "1.0", "proyecto": "V3",
            "csv": "", "datos_externos": "", "datos_sitio": "",
            "externos": {"luz_m": "2.0"}, "alcance": "perfil",
            "criterios": None, "sitio": None, "corridas": []}), encoding="utf-8")
        gapp.filedialog.askopenfilename = lambda **kw: str(vieja)
        ventana.cargar_sesion()
        raiz.update()
        r["tras_sesion_v3"] = {c: ventana.externos_vars[c].get()
                               for c in CAMPOS_NUEVOS + ("luz_m",)}
        # 4. Las entradas de la pestaña 1 invalidan el informe.
        import cli
        gestos = {
            "datos_sitio": lambda: ventana.datos_sitio_var.set("otro_sitio.json"),
            "externo": lambda: ventana.externos_vars["luz_m"].set("3,1"),
            "alcance": lambda: ventana.alcance_var.set(
                cli.ALCANCE_EXPEDIENTE if ventana.alcance_var.get() == cli.ALCANCE_PERFIL
                else cli.ALCANCE_PERFIL),
        }
        r["invalidacion"] = {}
        for nombre, gesto in gestos.items():
            ventana.csv_var.set(str(CSV_PERFIL))
            ventana.datos_sitio_var.set("")
            ventana.alcance_var.set(cli.ALCANCE_PERFIL)
            for c in ventana.externos_vars.values():
                c.set("")
            ventana.ejecutar_pipeline()
            raiz.update()
            corrio = ventana.informe is not None
            gesto()
            raiz.update()
            r["invalidacion"][nombre] = {
                "corrio": corrio, "informe_es_None": ventana.informe is None,
                "motivo": ventana.btn_json.motivo}
        # 5. (item 45, ficha C8-02) las discrepancias abiertas y la lista de
        #    corridas anteriores para comparar, en la pestaña 4.
        ventana.alcance_var.set(cli.ALCANCE_PERFIL)
        for c in ventana.externos_vars.values():
            c.set("")
        ventana.ejecutar_pipeline()
        raiz.update()
        r["comparar"] = {
            "discrepancias": ventana.lbl_discrepancias.cget("text"),
            "corridas": list(ventana.cmb_corridas.cget("values")),
            "boton_encendido": str(ventana.btn_comparar_corrida.cget("state")) == "normal",
            "elegida": ventana.corrida_a_comparar_var.get()}
        # La ventana de texto del resultado no se abre: se lee el objeto.
        ventana._mostrar_comparacion = lambda res, ruta: None
        resultado = ventana.comparar_con_corrida()
        r["comparar"]["iguales"] = None if resultado is None else resultado.iguales
        ventana.csv_var.set(str(CSV_PERFIL))
        raiz.update()
        r["comparar"]["tras_invalidar"] = {
            "corridas": list(ventana.cmb_corridas.cget("values")),
            "boton_encendido": str(ventana.btn_comparar_corrida.cget("state")) == "normal"}
        r["dialogos_de_error"] = [list(map(str, d)) for d in dialogos if d[0] == "error"]
    finally:
        raiz.destroy()

    (salida / "resumen_ve5.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(r, ensure_ascii=False)[:2000])
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[3])
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
