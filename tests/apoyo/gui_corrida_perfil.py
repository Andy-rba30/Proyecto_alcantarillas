"""
tests/apoyo/gui_corrida_perfil.py
=================================
Una corrida de PERFIL de punta a punta SOBRE LA VENTANA DE VERDAD, para que
`tests/test_gui_contrato.py` la lance en un proceso aparte.

    python -m tests.apoyo.gui_corrida_perfil <directorio de salida>

Por que es un modulo y no un test
---------------------------------
Porque tiene que correr en un proceso LIMPIO. `test_gui_contrato.py` instala
DOBLES de `tkinter` y de `ttkbootstrap` en `sys.modules` para poder importar
`gui/app.py` sin entorno grafico --- que es lo correcto para lo que esos tests
prueban ---, y una vez instalados no se pueden retirar: `gui.app` queda
importado contra ellos. Un test que despues quisiera levantar una ventana de
verdad recibiria el doble y construiria un espejismo. Lanzarlo aparte es lo
unico que garantiza que lo que se ejecuta es lo que el proyectista ejecuta.

Que se sustituye, y que no
--------------------------
Se sustituyen DOS cosas, las dos del lado del raton: el dialogo de «guardar
como» --- que es lo que el usuario rellena --- y los avisos modales, que
bloquearian un proceso sin nadie delante. `showerror` se sustituye por algo
que ABORTA: un exportador que se comiera su excepcion pasaria desapercibido de
cualquier otra forma, y ese es justamente el defecto que SIS-E-03 encontro.

Todo lo demas es el programa: la ventana se construye entera, los campos se
rellenan como los rellena el proyectista, y EJECUTAR es el mismo metodo que
cuelga del boton.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for _ruta in (str(RAIZ), str(RAIZ / "src")):
    if _ruta not in sys.path:
        sys.path.insert(0, _ruta)

import cli                                             # noqa: E402

CSV_PERFIL = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"

# Los datos externos del corredor. Son los mismos de
# `tests/test_cierre_perfil.py`: la corrida de la GUI y la de la CLI tienen
# que partir de la misma entrada o comparar sus salidas no significaria nada.
EXTERNOS = {
    "globales": {"luz_m": 3.0, "L_hidraulico_m": 120.0},
    "puntos": {"C-01": {"Q_m3s": 0.65, "S_conducto": 0.004}},
}


def main(salida: Path) -> int:
    import ttkbootstrap as tb

    import gui.app as gapp

    salida.mkdir(parents=True, exist_ok=True)
    externos = salida / "datos_externos.json"
    externos.write_text(json.dumps(EXTERNOS, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    raiz = tb.Window(themename="litera")
    try:
        ventana = gapp.ExpedienteApp(raiz)
        ventana.csv_var.set(str(CSV_PERFIL))
        ventana.datos_externos_var.set(str(externos))
        ventana.proyecto_var.set("cierre del nivel de perfil")
        ventana.alcance_var.set(cli.ALCANCE_PERFIL)

        ventana.ejecutar_pipeline()
        raiz.update()

        informe = ventana.informe
        if informe is None:
            print("ERROR: la GUI no produjo informe")
            return 1

        resumen = {
            "alcance": informe.alcance,
            "puntos": len(informe.puntos),
            "dimensionados": sorted(p.punto.id for p in informe.puntos
                                    if p.dimensionado),
            "diferidos": len(informe.diferidos()),
            "plantilla": ventana._plantilla().name,
            "criterios_bloqueantes": sorted(
                c.clave for c in cli.criterios_bloqueantes(informe)),
        }

        destinos = iter([salida / "memoria.html", salida / "resumen.csv",
                         salida / "informe.json"])
        gapp.filedialog.asksaveasfilename = lambda **kw: str(next(destinos))
        gapp.messagebox.showinfo = lambda *a, **k: None

        def _no_deberia(*a, **k):
            raise AssertionError(f"la GUI mostro un error: {a}")

        gapp.messagebox.showerror = _no_deberia

        ventana.exportar_html()
        ventana.exportar_csv()
        ventana.exportar_json()
    finally:
        raiz.destroy()

    (salida / "resumen_de_la_corrida.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[3])
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
