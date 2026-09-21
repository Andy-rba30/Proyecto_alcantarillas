"""
tests/apoyo/gui_ext10_real.py
=============================
EXT-10 SOBRE LA VENTANA DE VERDAD: dos obras, una obra vacia y abrir B
tras A, con el campo «JSON de datos de sitio» de la pestaña 1 y la sesion
de formato 3.

    python -m tests.apoyo.gui_ext10_real <directorio de salida>

Corre en un proceso limpio por la misma razon que `gui_contexto_real.py`:
`test_gui_contrato.py` instala dobles de `tkinter` y con ellos la ventana
seria un espejismo. Lo que se mide aqui es lo que ningun test de AST puede
ver: el valor REAL del campo de la pestaña 1 tras cargar una sesion, el
estado REAL de los exportadores, el archivo REAL que «Guardar sesion»
escribe (formato 3, con id, sitio y corridas), y que datos de sitio
gobiernan de verdad la corrida de la ventana.

Que se mide, en orden:

  1. obra A: sitio_A.json en el campo, corrida de expediente -> el PGA de
     la cadena sismica es el de A y el origen del JSON es sitio_A.json;
  2. «Guardar sesion» escribe un formato 3 con id, `sitio` con los [S] de A,
     `csv_sha1` y una corrida embebida con su `informe_json`;
  3. «Nuevo proyecto» (obra vacia): retira los [S] de A, vacia el campo, deja
     el informe en None y los exportadores apagados, y una corrida sin sitio
     gobierna con datos_sitio.py;
  4. cargar la sesion de B (otro PGA, por bloque `sitio`) tras A: el campo
     de la pestaña 1 y los [S] efectivos son los de B, el id es el de B y la
     corrida es la de B;
  5. un sitio.json con una clave mala se rechaza sin correr y sin traza.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

import cli                                             # noqa: E402
from src import datos_sitio as ds                      # noqa: E402
from src import sesion as ses                          # noqa: E402

CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"
FECHA = "2026-09-21"


def _sitio(pga, corredor):
    return {"PGA_roca_B": {"valor": pga, "trazabilidad": f"lectura A3 de {corredor}",
                           "fecha": FECHA},
            "corredor_del_proyecto": {"valor": corredor,
                                      "trazabilidad": f"expediente vial de {corredor}",
                                      "fecha": FECHA}}


def _exportadores(ventana):
    return {nombre: str(boton.cget("state")) == "normal"
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
    sitio_a = salida / "sitio_A.json"
    sitio_a.write_text(json.dumps(_sitio(0.40, "Obra A, km 0-4")), encoding="utf-8")
    dialogos = []
    gapp.messagebox.showinfo = lambda titulo, texto, *a, **k: dialogos.append(
        ("info", titulo, texto))
    gapp.messagebox.showerror = lambda titulo, texto, *a, **k: dialogos.append(
        ("error", titulo, texto))
    gapp.messagebox.askyesno = lambda *a, **k: True

    raiz = tb.Window(themename="litera")
    resumen = {}
    try:
        ventana = gapp.ExpedienteApp(raiz)
        ventana.csv_var.set(str(CSV_EJEMPLO))
        ventana.datos_externos_var.set(str(EXTERNOS))
        ventana.externos_vars["luz_m"].set("2,75")
        ventana.proyecto_var.set("Obra A")
        ventana.alcance_var.set(cli.ALCANCE_EXPEDIENTE)
        resumen["id_inicial"] = ventana.sesion_id

        # 1. Obra A por el campo de la pestaña 1.
        ventana.datos_sitio_var.set(str(sitio_a))
        informe = _correr(ventana, raiz)
        if informe is None:
            print("ERROR: la GUI no produjo informe con sitio_A")
            return 1
        volcado = cli.informe_json(informe)
        resumen["pga_A"] = volcado["cabezal"]["cadena_sismica"]["PGA"]
        resumen["origen_A"] = next(u["origen"] for u in volcado["datos_sitio"]["usados"]
                                   if u["clave"] == "PGA_roca_B")
        resumen["corredor_A"] = volcado["expediente"]["corredor_del_proyecto"]["valor"]
        resumen["exportadores_tras_A"] = _exportadores(ventana)

        # 2. Guardar sesion: formato 3.
        guardada = salida / "sesion_A.json"
        gapp.filedialog.asksaveasfilename = lambda **kw: str(guardada)
        ventana.guardar_sesion()
        data = json.loads(guardada.read_text(encoding="utf-8"))
        resumen["sesion_guardada"] = {
            "formato_version": data["formato_version"],
            "id": data["id"],
            "datos_sitio": data["datos_sitio"],
            "claves_sitio": sorted(data["sitio"]["valores"]),
            "csv_sha1": data["csv_sha1"],
            "corridas": len(data["corridas"]),
            "corrida_tiene_informe": "informe_json" in data["corridas"][0],
            "errores": ses.errores_de_sesion(data),
        }

        # 3. Nuevo proyecto: obra vacia.
        ventana.nuevo_proyecto()
        raiz.update()
        resumen["tras_nuevo"] = {
            "campo_sitio": ventana.datos_sitio_var.get(),
            "proyecto": ventana.proyecto_var.get(),
            "csv": ventana.csv_var.get(),
            "informe_es_None": ventana.informe is None,
            "exportadores": _exportadores(ventana),
            "declarados": ds.datos_declarados_en_caliente(),
            "id_cambio": ventana.sesion_id != data["id"],
            "corridas": len(ventana.corridas),
        }
        ventana.csv_var.set(str(CSV_EJEMPLO))
        ventana.datos_externos_var.set(str(EXTERNOS))
        ventana.externos_vars["luz_m"].set("2,75")
        ventana.alcance_var.set(cli.ALCANCE_EXPEDIENTE)
        informe = _correr(ventana, raiz)
        volcado = cli.informe_json(informe)
        resumen["pga_vacia"] = volcado["cabezal"]["cadena_sismica"]["PGA"]
        resumen["origen_vacia"] = next(u["origen"] for u in volcado["datos_sitio"]["usados"]
                                       if u["clave"] == "PGA_roca_B")

        # 4. Cargar la sesion de B tras A (por bloque `sitio`, sin archivo).
        sesion_b = ses.sesion_vacia(gapp.APP_VERSION)
        sesion_b.update({"proyecto": "Obra B", "csv": str(CSV_EJEMPLO),
                         "datos_externos": str(EXTERNOS), "datos_sitio": "",
                         "externos": {"luz_m": "2,75"},
                         "alcance": cli.ALCANCE_EXPEDIENTE,
                         "sitio": {"valores": _sitio(0.30, "Obra B, km 10-12")}})
        ruta_b = salida / "sesion_B.json"
        ruta_b.write_text(json.dumps(sesion_b), encoding="utf-8")
        gapp.filedialog.askopenfilename = lambda **kw: str(ruta_b)
        ventana.datos_sitio_var.set(str(sitio_a))     # A tecleada antes de abrir B
        ventana.cargar_sesion()
        raiz.update()
        resumen["tras_cargar_B"] = {
            "campo_sitio": ventana.datos_sitio_var.get(),
            "id": ventana.sesion_id,
            "id_esperado": sesion_b["id"],
            "declarados": ds.datos_declarados_en_caliente(),
            "pga_efectivo": ds.dato_efectivo("PGA_roca_B").valor,
            "origen": ds.origen_de("PGA_roca_B"),
            "informe_es_None": ventana.informe is None,
        }
        informe = _correr(ventana, raiz)
        volcado = cli.informe_json(informe)
        resumen["pga_B"] = volcado["cabezal"]["cadena_sismica"]["PGA"]
        resumen["corredor_B"] = volcado["expediente"]["corredor_del_proyecto"]["valor"]

        # 5. Un sitio.json malo se rechaza sin correr.
        malo = salida / "sitio_malo.json"
        malo.write_text(json.dumps({"PGA_rocaB": {"valor": 0.2, "trazabilidad": "t",
                                                  "fecha": FECHA}}), encoding="utf-8")
        ventana.datos_sitio_var.set(str(malo))
        dialogos.clear()
        informe = _correr(ventana, raiz)
        resumen["tras_malo"] = {
            "informe_es_None": ventana.informe is None,
            "error_visible": ventana.lbl_error_datos.cget("text"),
            "pga_efectivo": ds.dato_efectivo("PGA_roca_B").valor,
        }
    finally:
        raiz.destroy()

    (salida / "resumen_ext10.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[3])
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
