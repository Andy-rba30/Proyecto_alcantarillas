"""
tests/apoyo/gui_ui1_hidrologia_real.py
======================================
UI-1 SOBRE LA VENTANA DE VERDAD: la hidrologia en la pestaña 1 y en la
sesion de formato 4 (ficha T1-04, la parte de interfaz).

    python -m tests.apoyo.gui_ui1_hidrologia_real <directorio de salida>

Corre en un proceso limpio por la misma razon que `gui_ext10_real.py`:
`test_gui_contrato.py` instala dobles de `tkinter` y con ellos la ventana
seria un espejismo. Las entradas son DATOS DE PRUEBA: el CSV de ejemplo con
el `Q_m3s` de las tres obras con cuenca VACIADO (para que el caudal lo
calcule el programa) y las cuencas y la serie SINTETICAS de
`tests/fixtures/hidrologia/`.

Que se mide, en orden:

  1. el anticipo de la pestaña 1 sin hidrologia dice «DETIENE» del `Q_m3s`
     vacio, y con los dos campos llenos lo deja «espera» (depende de la
     hidrologia) --- refrescado por el gesto de escribir en los campos ---;
  2. con un solo campo, EJECUTAR no corre y dice el mensaje de
     `servicio.cargar_hidrologia`;
  3. con los dos, la corrida calcula el caudal: el detalle de la pestaña 3
     de una obra con cuenca dice «calculado», y el contexto lleva las dos
     huellas de los archivos que se leyeron;
  4. cambiar un campo invalida el informe y apaga los exportadores;
  5. el JSON del hijo del PDF (`cli.py --sesion` con la sesion que
     `_lanzar_pdf` arma) es el de la ventana, salvo la marca de tiempo;
  6. «Guardar sesion» escribe el formato 4 con las dos rutas;
  7. «Nuevo proyecto» vacia los dos campos; «Cargar sesion» los repone;
  8. una sesion de formato 3 de verdad (`tests/fixtures/sesion_v3/`) se abre
     sin hidrologia, corre, y al guardarla se reescribe en formato 4.
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

import cli                                             # noqa: E402
from src import criterios_adoptados as ca              # noqa: E402
from src import datos_sitio as ds                      # noqa: E402
from src import declaracion as dec                     # noqa: E402
from src import editores as sed                        # noqa: E402
from src import sesion as ses                          # noqa: E402
from src.modelos import ErrorProyecto                  # noqa: E402
from src.modulos.M11_reporte import sha1_archivo       # noqa: E402

CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"
HIDRO = RAIZ / "tests" / "fixtures" / "hidrologia"
CUENCAS = HIDRO / "cuencas_prueba.csv"
ESTACION = HIDRO / "estacion_prueba.csv"
SESION_V3 = RAIZ / "tests" / "fixtures" / "sesion_v3" / "sesion_v3_partida.json"
# Las obras del CSV de ejemplo que tienen fila en el CSV de cuencas de prueba.
OBRAS_CON_CUENCA = ("A-01", "A-02", "B-01")
OBRA_DEL_DETALLE = "A-02"


def _csv_sin_caudal(destino: Path) -> Path:
    """El CSV de ejemplo con el `Q_m3s` de las obras con cuenca vaciado."""
    with CSV_EJEMPLO.open(encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))
    for fila in filas:
        if fila["id"] in OBRAS_CON_CUENCA:
            fila["Q_m3s"] = ""
    with destino.open("w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    return destino


def _exportadores(ventana):
    # El grupo entero, de la tupla de la ventana (UI-2): siete desde la
    # memoria resumida.
    import gui.app as gapp
    return {nombre.removeprefix("btn_"): {
        "encendido": str(getattr(ventana, nombre).cget("state")) == "normal",
        "motivo": getattr(ventana, nombre).motivo}
        for nombre in gapp.BOTONES_DE_EXPORTACION}


def _filas_del_prevuelo(ventana):
    return [list(ventana.tree_prevuelo.item(i, "values"))
            for i in ventana.tree_prevuelo.get_children()]


def _caudal_en_el_prevuelo(ventana):
    """El estado y la etapa del `Q_m3s` de cada obra con cuenca, en el anticipo."""
    salida = {}
    for fila in _filas_del_prevuelo(ventana):
        punto, dato, estado, etapa = fila[0], fila[1], fila[2], fila[3]
        identificador = punto.split(" ")[0]
        if dato == "Q_m3s" and identificador in OBRAS_CON_CUENCA:
            salida[identificador] = {"estado": estado, "etapa": etapa}
    return salida


def _correr(ventana, raiz):
    ventana.ejecutar_pipeline()
    raiz.update()
    return ventana.informe


def _sin_marca(datos):
    return ses.sin_marca_de_tiempo(json.loads(json.dumps(datos, ensure_ascii=False,
                                                         allow_nan=False)))


def main(salida: Path) -> int:
    import ttkbootstrap as tb

    import gui.app as gapp
    import gui.exportacion_pdf as expdf

    salida.mkdir(parents=True, exist_ok=True)
    puntos = _csv_sin_caudal(salida / "puntos_sin_caudal.csv")
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
        ventana.proyecto_var.set("DATOS DE PRUEBA - UI-1")
        ventana.datos_externos_var.set(str(EXTERNOS))
        ventana.externos_vars["luz_m"].set("2,75")
        ventana.alcance_var.set(cli.ALCANCE_PERFIL)
        ventana.csv_var.set(str(puntos))
        raiz.update()
        # El criterio FEN, por la MISMA puerta que «Aplicar» de la pestaña 2.
        sed.declarar("homogeneidad_serie_fen", "serie_completa")
        ventana._llenar_tabla_criterios()
        raiz.update()

        # 1. El anticipo, antes y despues de llenar los dos campos.
        r["prevuelo_sin_hidrologia"] = _caudal_en_el_prevuelo(ventana)
        ventana.cuencas_var.set(str(CUENCAS))
        ventana.estacion_var.set(str(ESTACION))
        raiz.update()
        r["prevuelo_con_hidrologia"] = _caudal_en_el_prevuelo(ventana)

        # 2. Un solo campo: no corre y lo dice con el mensaje del servicio.
        ventana.estacion_var.set("")
        raiz.update()
        r["prevuelo_un_campo"] = ventana.lbl_anticipo_prevuelo.cget("text")
        informe = _correr(ventana, raiz)
        r["un_campo"] = {"informe_es_None": informe is None,
                         "error_visible": ventana.lbl_error_datos.cget("text"),
                         "exportadores": _exportadores(ventana)}
        try:
            cli.cargar_hidrologia(CUENCAS, None)
        except ErrorProyecto as exc:
            r["mensaje_del_servicio"] = str(exc)

        # 3. Los dos campos: el caudal sale calculado.
        ventana.estacion_var.set(str(ESTACION))
        raiz.update()
        informe = _correr(ventana, raiz)
        if informe is None:
            print("ERROR: la ventana no produjo informe con la hidrologia:",
                  ventana.lbl_error_datos.cget("text"))
            return 1
        r["exportadores_tras_correr"] = _exportadores(ventana)
        r["contexto"] = {"cuencas_sha1": informe.contexto.cuencas_sha1,
                         "estacion_sha1": informe.contexto.estacion_sha1,
                         "cuencas_sha1_del_archivo": sha1_archivo(CUENCAS),
                         "estacion_sha1_del_archivo": sha1_archivo(ESTACION)}
        punto = next(p for p in informe.puntos if p.punto.id == OBRA_DEL_DETALLE)
        r["caudal"] = {"calculado": bool(punto.caudal and punto.caudal.calculado),
                       "leyenda": punto.caudal.leyenda if punto.caudal else ""}
        ventana.tree_puntos.selection_set(OBRA_DEL_DETALLE)
        ventana.tree_puntos.see(OBRA_DEL_DETALLE)
        raiz.update()
        r["detalle"] = ventana.txt_detalle.get("1.0", "end").strip()
        r["lineas_de_la_cli"] = list(cli._lineas_punto(punto))
        r["entradas_de_la_corrida"] = dict(ventana.entradas_de_la_corrida)
        volcado_ventana = cli.informe_json(informe)
        r["json_ventana_hidrologia"] = volcado_ventana["expediente"].get("hidrologia")

        # 5. El hijo del PDF: la sesion que `_lanzar_pdf` arma, por la CLI.
        sesion_hijo = expdf.sesion_de_la_corrida(
            informe, proyecto=ventana.proyecto_de_la_corrida,
            formato_version=gapp.FORMATO_SESION, app_version=gapp.APP_VERSION,
            id_sesion=ventana.sesion_id, **ventana.entradas_de_la_corrida)
        ruta_hijo = salida / "sesion_del_hijo.json"
        ses.escribir_json_atomico(ruta_hijo, sesion_hijo)
        json_hijo = salida / "informe_del_hijo.json"
        hecho = subprocess.run(
            [sys.executable, str(RAIZ / "cli.py"), "--sesion", str(ruta_hijo),
             "--json", str(json_hijo)],
            cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", timeout=900)
        r["hijo"] = {"codigo": hecho.returncode,
                     "stderr": hecho.stderr[-2000:],
                     "sesion_cuencas": sesion_hijo.get("cuencas"),
                     "sesion_estacion": sesion_hijo.get("estacion")}
        if json_hijo.is_file():
            ajeno = json.loads(json_hijo.read_text(encoding="utf-8"))
            r["hijo"]["mismo_json"] = _sin_marca(volcado_ventana) == _sin_marca(ajeno)
            r["hijo"]["hidrologia"] = ajeno["expediente"].get("hidrologia")

        # 4. Cambiar un campo invalida el informe.
        ventana.cuencas_var.set(str(CUENCAS))
        raiz.update()
        r["tras_cambiar_cuencas"] = {"informe_es_None": ventana.informe is None,
                                     "exportadores": _exportadores(ventana),
                                     "barra": ventana.lbl_estado.cget("text")}
        informe = _correr(ventana, raiz)
        ventana.estacion_var.set(str(ESTACION))
        raiz.update()
        r["tras_cambiar_estacion"] = {"informe_es_None": ventana.informe is None}
        informe = _correr(ventana, raiz)

        # 6. Guardar sesion: formato 4 con las dos rutas.
        guardada = salida / "sesion_ui1.json"
        gapp.filedialog.asksaveasfilename = lambda **kw: str(guardada)
        ventana.guardar_sesion()
        data = json.loads(guardada.read_text(encoding="utf-8"))
        r["sesion_guardada"] = {"formato_version": data["formato_version"],
                                "cuencas": data.get("cuencas"),
                                "estacion": data.get("estacion"),
                                "errores": ses.errores_de_sesion(data)}

        # 7. Nuevo proyecto vacia; Cargar sesion repone.
        ventana.nuevo_proyecto()
        raiz.update()
        r["tras_nuevo"] = {"cuencas": ventana.cuencas_var.get(),
                           "estacion": ventana.estacion_var.get(),
                           "informe_es_None": ventana.informe is None}
        gapp.filedialog.askopenfilename = lambda **kw: str(guardada)
        ventana.cargar_sesion()
        raiz.update()
        r["tras_cargar"] = {"cuencas": ventana.cuencas_var.get(),
                            "estacion": ventana.estacion_var.get(),
                            "csv": ventana.csv_var.get(),
                            "informe_es_None": ventana.informe is None}

        # 8. Una sesion de formato 3 de verdad.
        dialogos.clear()
        gapp.filedialog.askopenfilename = lambda **kw: str(SESION_V3)
        ventana.cargar_sesion()
        raiz.update()
        v3 = json.loads(SESION_V3.read_text(encoding="utf-8"))
        r["tras_cargar_v3"] = {
            "cuencas": ventana.cuencas_var.get(),
            "estacion": ventana.estacion_var.get(),
            "proyecto_igual": ventana.proyecto_var.get() == v3["proyecto"],
            "csv_igual": ventana.csv_var.get() == v3["csv"],
            "externos_igual": ventana.datos_externos_var.get() == v3["datos_externos"],
            "sitio_igual": ventana.datos_sitio_var.get() == v3["datos_sitio"],
            "alcance": ventana.alcance_var.get(),
            "id_igual": ventana.sesion_id == v3["id"],
            "corridas": len(ventana.corridas),
            "criterios_declarados": sorted(ca.valores_dinamicos()),
            "procedencias": sorted(dec.procedencias()),
            "sitio_declarado": sorted(ds.datos_declarados_en_caliente()),
            "externos": {clave: var.get() for clave, var in ventana.externos_vars.items()},
            "dialogos": [[d[0], d[1]] for d in dialogos],
            "errores_en_dialogos": [d for d in dialogos if d[0] == "error"],
        }
        informe = _correr(ventana, raiz)
        r["corrida_v3"] = {"informe": informe is not None,
                           "hidrologia_es_None": (informe is None
                                                  or informe.hidrologia is None),
                           "error_visible": ventana.lbl_error_datos.cget("text")}
        guardada_v3 = salida / "sesion_v3_reescrita.json"
        gapp.filedialog.asksaveasfilename = lambda **kw: str(guardada_v3)
        ventana.guardar_sesion()
        data = json.loads(guardada_v3.read_text(encoding="utf-8"))
        r["v3_reescrita"] = {"formato_version": data["formato_version"],
                             "cuencas": data.get("cuencas"),
                             "estacion": data.get("estacion"),
                             "id_igual": data["id"] == v3["id"],
                             "corridas": len(data["corridas"]),
                             "errores": ses.errores_de_sesion(data)}
    finally:
        raiz.destroy()

    (salida / "resumen_ui1.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in r.items() if k != "detalle"}, ensure_ascii=False)[:4000])
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[3])
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
