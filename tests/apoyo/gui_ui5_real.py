"""
tests/apoyo/gui_ui5_real.py
===========================
UI-5 SOBRE LA VENTANA DE VERDAD: cambiar el CSV de puntos invalida el
informe vigente, como la hidrologia (decision del dueño del 2026-11-15, ficha
UI1-01), y la memoria resumida en HTML que la ventana escribe dice de su
completa lo que es cierto (ficha UI2-01 b).

    python -m tests.apoyo.gui_ui5_real <directorio de salida>

Corre en un proceso limpio por la misma razon que `gui_contexto_real.py`:
`test_gui_contrato.py` instala dobles de `tkinter`. Lo que se mide aqui es lo
que el doble no puede ver: la traza REAL de Tk sobre el campo, que avisa en
cada escritura, el estado REAL de los siete exportadores, la barra y el panel
del cabezal del proyecto.

Que se mide, en orden (`tests/test_ui5_decisiones.py` lo juzga):

  0. sin informe, escribir en el campo del CSV no pinta otro motivo;
  1. una corrida, y TECLEAR otra ruta en el campo, letra a letra;
  2. otra corrida, y «Examinar…» con la MISMA ruta;
  3. otra corrida, y la misma ruta tecleada otra vez (borrar y escribir);
  4. otra corrida: los siete se encienden de nuevo;
  5. la frontera de la decision: cambiar el JSON de datos externos NO
     invalida (EXT-8);
  6. otra corrida, y «Cargar sesion» con otro CSV: el motivo es el de la
     sesion, no el del CSV;
  7. otra corrida, y «Nuevo proyecto»: lo mismo;
  8. otra corrida, y las dos memorias en HTML desde los botones: la completa y
     la resumida, del mismo informe;
  9. la pestaña 2 con «Solo los que bloquearon esta corrida» (revision de
     UI-5, H2): tras cambiar el CSV, tras cambiar el CSV de cuencas y tras
     una corrida que falla, la tabla, la linea de su ambito y la barra;
 10. un borrador de la pestaña 2 (un valor tecleado y sin aplicar) tras los
     mismos tres gestos (verificacion de UI-5, N2);
 11. y tras abrir otra obra, con «Cargar sesion» y con «Nuevo proyecto», que
     no lo heredan (N5).

DATOS DE PRUEBA: el CSV de perfil de ejemplo y unos datos externos de sonda.
"""

import json
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

import cli                                             # noqa: E402

CSV_PERFIL = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"
EXTERNOS = {
    "globales": {"luz_m": 3.0, "L_hidraulico_m": 120.0},
    "puntos": {"C-01": {"Q_m3s": 0.65, "S_conducto": 0.004}},
}


def _exportadores(ventana):
    import gui.app as gapp
    return {nombre.removeprefix("btn_"): {
        "encendido": str(getattr(ventana, nombre).cget("state")) == "normal",
        "motivo": getattr(ventana, nombre).motivo}
        for nombre in gapp.BOTONES_DE_EXPORTACION}


def _correr(ventana, raiz):
    ventana.ejecutar_pipeline()
    raiz.update()
    if ventana.informe is None:
        raise RuntimeError("la corrida no produjo informe: "
                           + ventana.lbl_error_datos.cget("text"))


def _estado(ventana, raiz):
    raiz.update()
    return {"informe_es_None": ventana.informe is None,
            "exportadores": _exportadores(ventana),
            "barra": ventana.lbl_estado.cget("text"),
            "cabezal": ventana.lbl_cabezal.cget("text"),
            "filas_puntos": len(ventana.tree_puntos.get_children()),
            "csv": ventana.csv_var.get()}


def _entrada_de(raiz, variable):
    """El `Entry` de la pestaña 1 ligado a `variable`: el que el usuario teclea."""
    pendientes = [raiz]
    while pendientes:
        w = pendientes.pop()
        pendientes.extend(w.winfo_children())
        try:
            if str(w.cget("textvariable")) == str(variable):
                return w
        except Exception:                       # widget sin esa opcion
            continue
    raise RuntimeError(f"no hay campo ligado a {variable}")


def _teclear(entrada, raiz, texto):
    """Borrar el campo y escribir `texto` letra a letra, como el usuario."""
    entrada.delete(0, "end")
    raiz.update()
    for letra in texto:
        entrada.insert("end", letra)
    raiz.update()


def main(salida: Path) -> int:
    import ttkbootstrap as tb

    import gui.app as gapp

    salida.mkdir(parents=True, exist_ok=True)
    externos = salida / "datos_externos.json"
    externos.write_text(json.dumps(EXTERNOS, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    otro_externos = salida / "otros_datos_externos.json"
    shutil.copyfile(externos, otro_externos)
    otro_csv = salida / "otra_copia_del_csv.csv"
    shutil.copyfile(CSV_PERFIL, otro_csv)
    dialogos = []
    gapp.messagebox.showinfo = lambda titulo, texto, *a, **k: dialogos.append(
        ("info", titulo, texto))
    gapp.messagebox.showerror = lambda titulo, texto, *a, **k: dialogos.append(
        ("error", titulo, texto))
    gapp.messagebox.askyesno = lambda *a, **k: True

    raiz = tb.Window(themename="litera")
    r = {}
    try:
        ventana = gapp.ExpedienteApp(raiz)
        campo_csv = _entrada_de(raiz, ventana.csv_var)

        def preparar():
            ventana.csv_var.set(str(CSV_PERFIL))
            ventana.datos_externos_var.set(str(externos))
            ventana.proyecto_var.set("DATOS DE PRUEBA - UI-5")
            ventana.alcance_var.set(cli.ALCANCE_PERFIL)
            raiz.update()

        # 0. Sin informe: el gesto no pinta otro motivo.
        preparar()
        _teclear(campo_csv, raiz, str(otro_csv))
        r["sin_informe"] = _exportadores(ventana)

        # 1. Teclear otra ruta.
        preparar()
        _correr(ventana, raiz)
        r["tras_correr"] = _exportadores(ventana)
        _teclear(campo_csv, raiz, str(otro_csv))
        r["tras_teclear"] = _estado(ventana, raiz)

        # 2. «Examinar…» con la MISMA ruta.
        preparar()
        _correr(ventana, raiz)
        gapp.filedialog.askopenfilename = lambda **kw: str(CSV_PERFIL)
        ventana._elegir_csv()
        r["tras_examinar_la_misma"] = _estado(ventana, raiz)

        # 3. La misma ruta tecleada otra vez.
        preparar()
        _correr(ventana, raiz)
        _teclear(campo_csv, raiz, str(CSV_PERFIL))
        r["tras_teclear_la_misma"] = _estado(ventana, raiz)

        # 4. Volver a correr enciende los siete.
        _correr(ventana, raiz)
        r["tras_volver_a_correr"] = _exportadores(ventana)

        # 5. La frontera: el JSON de datos externos no invalida.
        ventana.datos_externos_var.set(str(otro_externos))
        r["tras_cambiar_externos"] = _estado(ventana, raiz)

        # 6. «Cargar sesion» con otro CSV: el motivo es el de la sesion.
        preparar()
        _correr(ventana, raiz)
        sesion = salida / "sesion_b.json"
        r["csv_de_la_sesion"] = str(otro_csv)
        sesion.write_text(json.dumps({
            "formato_version": gapp.FORMATO_SESION, "app_version": "1.0",
            "proyecto": "obra B", "csv": str(otro_csv),
            "datos_externos": str(externos), "externos": {},
            "alcance": cli.ALCANCE_PERFIL,
            "criterios": {"valores": {}, "procedencias": {}},
        }), encoding="utf-8")
        gapp.filedialog.askopenfilename = lambda **kw: str(sesion)
        ventana.cargar_sesion()
        r["tras_cargar_sesion"] = _estado(ventana, raiz)

        # 7. «Nuevo proyecto».
        preparar()
        _correr(ventana, raiz)
        ventana.nuevo_proyecto()
        r["tras_nuevo_proyecto"] = _estado(ventana, raiz)

        # 8. Las dos memorias en HTML, desde sus botones, del mismo informe.
        preparar()
        _correr(ventana, raiz)
        for nombre, boton in (("completa.html", ventana.btn_html),
                              ("resumida.html", ventana.btn_html_resumida)):
            gapp.filedialog.asksaveasfilename = (
                lambda _n=nombre, **kw: str(salida / _n))
            boton.boton.invoke()
            raiz.update()
        r["memorias_html"] = {n: (salida / n).is_file()
                              for n in ("completa.html", "resumida.html")}

        # 9. La pestaña 2 con «Solo los que bloquearon esta corrida» (revision
        #    de UI-5, H2): cada gesto que retira el informe la repinta sin el
        #    filtro de una corrida que ya no existe.
        from src import criterios_adoptados as ca
        bloqueantes = next(rotulo for rotulo, tag in gapp.FILTROS_DE_AMBITO
                           if tag == gapp.AMBITO_BLOQUEANTES)

        def tabla():
            raiz.update()
            return {"informe_es_None": ventana.informe is None,
                    "filas": len(ventana.tree_criterios_todos.get_children()),
                    "ambito": ventana.lbl_ambito.cget("text"),
                    "barra": ventana.lbl_estado.cget("text")}

        f = {"total_criterios": len(ca.CRITERIOS)}
        preparar()
        _correr(ventana, raiz)
        ventana.filtro_ambito_var.set(bloqueantes)
        f["con_corrida"] = tabla()
        _teclear(campo_csv, raiz, str(otro_csv))
        f["tras_csv"] = tabla()
        preparar()
        _correr(ventana, raiz)
        ventana.cuencas_var.set(str(salida / "cuencas_cualquiera.csv"))
        f["tras_cuencas"] = tabla()
        ventana.cuencas_var.set("")
        preparar()
        _correr(ventana, raiz)
        # Una corrida que falla al cargar, sin otro gesto antes: el JSON de
        # datos externos no invalida (la frontera de arriba), y apunta a un
        # archivo que no existe.
        ventana.datos_externos_var.set(str(salida / "no_existe.json"))
        ventana.ejecutar_pipeline()
        f["tras_corrida_fallida"] = tabla()
        ventana.filtro_ambito_var.set(gapp.FILTROS_DE_AMBITO[0][0])
        r["filtro_bloqueantes"] = f

        # 10. Un borrador de la pestaña 2 --- un valor tecleado y sin aplicar
        #     --- sobrevive a cada gesto que retira el informe (verificacion
        #     de UI-5, N2).
        clave = "HW_D_max"
        b = {"archivo": ventana._literal_de(ca.criterio(clave).valor)}

        def con_borrador(gesto):
            preparar()
            ventana.datos_externos_var.set(str(externos))
            _correr(ventana, raiz)
            ventana.tree_criterios_todos.selection_set(clave)
            raiz.update()
            ventana.valor_declarado_var.set("1.3")
            raiz.update()
            gesto()
            raiz.update()
            return {"informe_es_None": ventana.informe is None,
                    "borrador": ventana.valor_declarado_var.get()}

        b["tras_csv"] = con_borrador(lambda: _teclear(campo_csv, raiz, str(otro_csv)))
        b["tras_cuencas"] = con_borrador(
            lambda: ventana.cuencas_var.set(str(salida / "cuencas_cualquiera.csv")))
        ventana.cuencas_var.set("")

        def falla():
            ventana.datos_externos_var.set(str(salida / "no_existe.json"))
            ventana.ejecutar_pipeline()

        b["tras_corrida_fallida"] = con_borrador(falla)

        # 11. Pero abrir OTRA obra no hereda el borrador de la anterior
        #     (verificacion de UI-5, N5): «Cargar sesion» con una sesion que no
        #     declara el criterio, y «Nuevo proyecto»; el valor efectivo es el
        #     mismo en las dos obras.
        sesion_c = salida / "sesion_c.json"
        sesion_c.write_text(json.dumps({
            "formato_version": gapp.FORMATO_SESION, "app_version": "1.0",
            "proyecto": "obra C", "csv": str(CSV_PERFIL),
            "datos_externos": str(externos), "externos": {},
            "alcance": cli.ALCANCE_PERFIL,
            "criterios": {"valores": {}, "procedencias": {}},
        }), encoding="utf-8")

        def cargar_otra():
            gapp.filedialog.askopenfilename = lambda **kw: str(sesion_c)
            ventana.cargar_sesion()

        b["tras_cargar_otra_obra"] = con_borrador(cargar_otra)
        b["tras_nuevo_proyecto"] = con_borrador(ventana.nuevo_proyecto)
        r["borrador"] = b
        r["dialogos_de_error"] = [d for d in dialogos if d[0] == "error"]
    finally:
        raiz.destroy()

    (salida / "resumen_ui5.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(r, ensure_ascii=False)[:2000])
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[3])
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
