"""
tests/apoyo/gui_contexto_real.py
================================
EXT-4 SOBRE LA VENTANA DE VERDAD: el informe es de su corrida (PC-15) y
«Etapas bloqueadas» es la misma cuenta que la de la CLI (EXT-G-02).

    python -m tests.apoyo.gui_contexto_real <directorio de salida>

Corre en un proceso limpio por la misma razon que `gui_corrida_perfil.py`:
`test_gui_contrato.py` instala dobles de `tkinter` y con ellos la ventana
seria un espejismo. Lo que se mide aqui es lo que ningun test de AST puede
ver: el texto REAL de la etiqueta «Etapas bloqueadas», el estado REAL de los
cuatro botones de exportacion y el texto REAL de su tooltip tras cada gesto.

Que se mide, en orden:

  1. una corrida de perfil: la etiqueta «Etapas bloqueadas» de la pestaña 4
     dice lo mismo que la linea del volcado de la CLI sobre EL MISMO informe;
  2. declarar un criterio desde la pestaña 2 deja `informe` en None y los
     cuatro exportadores apagados diciendo por que;
  3. otra corrida, y quitar la declaracion: lo mismo;
  4. otra corrida, y cargar una sesion: lo mismo, y la sesion SUSTITUYE lo
     declarado (la clave de la obra anterior se retira);
  5. una corrida FALLIDA (CSV inexistente): no queda informe vigente y los
     exportadores dicen que la corrida no produjo informe;
  6. una sesion deformada (`"externos": null`) se rechaza con dialogo y no
     toca el nombre del proyecto ni el CSV.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for _ruta in (str(RAIZ), str(RAIZ / "src")):
    if _ruta not in sys.path:
        sys.path.insert(0, _ruta)

import cli                                             # noqa: E402
import criterios_adoptados as ca                       # noqa: E402

CSV_PERFIL = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"
EXTERNOS = {
    "globales": {"luz_m": 3.0, "L_hidraulico_m": 120.0},
    "puntos": {"C-01": {"Q_m3s": 0.65, "S_conducto": 0.004}},
}
CLAVE = "phi_relleno_trasdos"     # un vacio de Fase 9 que el perfil no invoca


def _exportadores(ventana):
    return {nombre: {"encendido": str(boton.cget("state")) == "normal",
                     "motivo": boton.motivo}
            for nombre, boton in (("json", ventana.btn_json),
                                  ("html", ventana.btn_html),
                                  ("pdf", ventana.btn_pdf),
                                  ("csv", ventana.btn_csv))}


def _correr(ventana, raiz):
    ventana.ejecutar_pipeline()
    raiz.update()
    return ventana.informe


def main(salida: Path) -> int:
    import ttkbootstrap as tb

    import gui.app as gapp

    salida.mkdir(parents=True, exist_ok=True)
    externos = salida / "datos_externos.json"
    externos.write_text(json.dumps(EXTERNOS, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    dialogos = []
    gapp.messagebox.showinfo = lambda titulo, texto, *a, **k: dialogos.append(
        ("info", titulo, texto))
    gapp.messagebox.showerror = lambda titulo, texto, *a, **k: dialogos.append(
        ("error", titulo, texto))

    raiz = tb.Window(themename="litera")
    resumen = {}
    try:
        ventana = gapp.ExpedienteApp(raiz)
        ventana.csv_var.set(str(CSV_PERFIL))
        ventana.datos_externos_var.set(str(externos))
        ventana.proyecto_var.set("contexto de corrida")
        ventana.alcance_var.set(cli.ALCANCE_PERFIL)

        # 1. La cuenta de la GUI contra la de la CLI, sobre el mismo informe.
        informe = _correr(ventana, raiz)
        if informe is None:
            print("ERROR: la GUI no produjo informe")
            return 1
        linea_cli = next(l for l in cli._lineas_resumen(informe)
                         if l.startswith("Etapas bloqueadas"))
        resumen["gui_etapas_bloqueadas"] = ventana.lbl_resumen[
            "Etapas bloqueadas"].cget("text")
        resumen["cli_etapas_bloqueadas"] = linea_cli.split(":")[1].strip()
        resumen["gui_diferidas"] = ventana.lbl_resumen[
            "Diferidas por alcance"].cget("text")
        resumen["informe_bloqueos_reales"] = len(informe.bloqueos_reales())
        resumen["informe_bloqueos_totales"] = len(informe.bloqueos())
        resumen["exportadores_tras_correr"] = _exportadores(ventana)
        resumen["barra_tras_correr"] = ventana.lbl_estado.cget("text")
        # La columna de bloqueos POR PUNTO de la pestaña 3: la cuenta real.
        resumen["columna_bloqueos"] = {
            iid: int(ventana.tree_puntos.set(iid, "bloqueos"))
            for iid in ventana.tree_puntos.get_children()}
        resumen["bloqueos_reales_por_punto"] = {
            p.punto.id: len(p.bloqueos_reales()) for p in informe.puntos}
        resumen["bloqueos_totales_por_punto"] = {
            p.punto.id: len(p.bloqueos) for p in informe.puntos}
        # El nombre del proyecto se lee AL CORRER: cambiarlo despues no
        # cambia la memoria que se exporta.
        ventana.proyecto_var.set("otro nombre tecleado despues de correr")
        destino_html = salida / "memoria_tras_cambiar_nombre.html"
        gapp.filedialog.asksaveasfilename = lambda **kw: str(destino_html)
        ventana.exportar_html()
        resumen["proyecto_en_la_memoria"] = (
            "contexto de corrida" in destino_html.read_text(encoding="utf-8"))
        resumen["otro_nombre_en_la_memoria"] = (
            "otro nombre tecleado" in destino_html.read_text(encoding="utf-8"))

        # 2. Declarar invalida.
        ventana._clave_criterio_seleccionado = CLAVE
        ventana.valor_declarado_var.set("32")
        ventana._aplicar_valor_corrida()
        raiz.update()
        resumen["informe_tras_declarar"] = ventana.informe is None
        resumen["exportadores_tras_declarar"] = _exportadores(ventana)
        resumen["barra_tras_declarar"] = ventana.lbl_estado.cget("text")
        resumen["filas_puntos_tras_declarar"] = len(
            ventana.tree_puntos.get_children())

        # 3. Quitar invalida.
        _correr(ventana, raiz)
        ventana._clave_criterio_seleccionado = CLAVE
        ventana._quitar_valor_corrida()
        raiz.update()
        resumen["informe_tras_quitar"] = ventana.informe is None
        resumen["exportadores_tras_quitar"] = _exportadores(ventana)

        # 4. Cargar sesion invalida y SUSTITUYE. Un externo tecleado antes
        # y ausente en la sesion se repone a vacio.
        ca.establecer_valor_dinamico(CLAVE, 30.0)
        _correr(ventana, raiz)
        primer_externo = next(iter(ventana.externos_vars))
        ventana.externos_vars[primer_externo].set("7")
        sesion = salida / "sesion_b.json"
        sesion.write_text(json.dumps({
            "formato_version": gapp.FORMATO_SESION, "app_version": "1.0",
            "proyecto": "obra B", "csv": str(CSV_PERFIL),
            "datos_externos": str(externos), "externos": {},
            "alcance": cli.ALCANCE_PERFIL,
            "criterios": {"valores": {"ke_entrada": 0.5}, "procedencias": {}},
        }), encoding="utf-8")
        gapp.filedialog.askopenfilename = lambda **kw: str(sesion)
        ventana.cargar_sesion()
        raiz.update()
        resumen["informe_tras_cargar"] = ventana.informe is None
        resumen["exportadores_tras_cargar"] = _exportadores(ventana)
        resumen["declarados_tras_cargar"] = sorted(ca.valores_dinamicos())
        resumen["proyecto_tras_cargar"] = ventana.proyecto_var.get()
        resumen["externo_ausente_tras_cargar"] = ventana.externos_vars[
            primer_externo].get()

        # 5. Una corrida fallida no deja informe vigente.
        _correr(ventana, raiz)
        ventana.csv_var.set(str(salida / "no_existe.csv"))
        raiz.update()
        _correr(ventana, raiz)
        resumen["informe_tras_fallo"] = ventana.informe is None
        resumen["exportadores_tras_fallo"] = _exportadores(ventana)
        resumen["barra_tras_fallo"] = ventana.lbl_estado.cget("text")

        # 6. Una sesion deformada se rechaza entera.
        ventana.proyecto_var.set("antes de la sesion rota")
        rota = salida / "sesion_rota.json"
        rota.write_text(json.dumps({"proyecto": "rota", "csv": "x.csv",
                                    "externos": None}), encoding="utf-8")
        gapp.filedialog.askopenfilename = lambda **kw: str(rota)
        dialogos.clear()
        ventana.cargar_sesion()
        raiz.update()
        resumen["proyecto_tras_sesion_rota"] = ventana.proyecto_var.get()
        resumen["dialogo_sesion_rota"] = [d[0] for d in dialogos]
    finally:
        raiz.destroy()

    (salida / "resumen_contexto.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[3])
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
