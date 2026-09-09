"""
tests/apoyo/gui_ayuda_real.py
=============================
La ayuda de entrada, abierta sobre una ventana DE VERDAD, para que
`tests/test_gui_contrato.py` la lance en un proceso aparte.

    python -m tests.apoyo.gui_ayuda_real <archivo de salida .json>

Que se ejercita, y por que no basta con el contrato del AST
-----------------------------------------------------------
`test_ayuda_entrada.py` comprueba el CONTENIDO --- que las 19 columnas salen
del censo y no de una lista escrita --- y `test_gui_contrato.py` comprueba el
CABLEADO leyendo el arbol. Entre las dos queda un hueco que solo un `Tk` real
cubre: que la ventana SE CONSTRUYA. Un `grid` mal puesto, un `iid` repetido en
el `Treeview` o un nombre de atributo mal escrito no se ven en el AST y revientan
al abrirla.

Y hay una cosa mas que solo se ve con el bucle de eventos corriendo: el detalle
de una columna cuelga de `<<TreeviewSelect>>`, que Tk ENCOLA. Con
`update_idletasks()` el manejador todavia no ha corrido y el panel se lee
vacio; hace falta `update()`. Es la misma leccion que
`gui/app.py::_reponer_seleccion` tiene escrita, y se volvio a tropezar con ella
al escribir esto --- por eso queda dicha aqui tambien.

Se ejercita ademas la REUTILIZACION de la ventana: dos clics seguidos en los
dos iconos tienen que dar la MISMA ventana con la pestana cambiada, y no dos
ventanas apiladas.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SRC = RAIZ / "src"
for _ruta in (RAIZ, SRC):
    if str(_ruta) not in sys.path:
        sys.path.insert(0, str(_ruta))

# La columna con la que se prueba el panel de detalle. Se elige la de
# `resolucion` mas larga del censo --- 1236 caracteres --- porque es la que
# obliga al panel a tener scroll, que es el defecto que la pestana 2 ya tuvo.
COLUMNA_DE_DETALLE = "sucs_fundacion"


def main(destino: Path) -> int:
    import tkinter as tk

    import gui.ayuda_entrada as ayuda_gui
    from gui.app import ExpedienteApp

    raiz = tk.Tk()
    raiz.withdraw()
    obs = {}
    try:
        for pestana in (ayuda_gui.PESTANA_CSV, ayuda_gui.PESTANA_JSON):
            v = ayuda_gui.VentanaAyudaEntrada(raiz, pestana)
            v.update()
            obs[f"pestana_activa_{pestana}"] = v.nb.tab(
                v.nb.select(), "text").strip()
            obs[f"filas_csv_{pestana}"] = list(v.tree_csv.get_children())
            obs[f"filas_json_{pestana}"] = list(v.tree_json.get_children())

            # El detalle responde a la SELECCION REAL, con `update()` para que
            # el bucle procese el evento encolado.
            v.tree_csv.selection_set(COLUMNA_DE_DETALLE)
            v.update()
            obs[f"detalle_{pestana}"] = v.txt_csv.get("1.0", "end").strip()
            v.destroy()

        # Los dos iconos de la ventana principal, sobre la misma ayuda.
        app = ExpedienteApp(tk.Toplevel(raiz))
        app.root.withdraw()
        raiz.update()
        primera = app._abrir_ayuda(ayuda_gui.PESTANA_CSV)
        segunda = app._abrir_ayuda(ayuda_gui.PESTANA_JSON)
        raiz.update()
        obs["misma_ventana"] = primera is segunda
        obs["pestana_tras_el_segundo_icono"] = primera.nb.tab(
            primera.nb.select(), "text").strip()
        primera.destroy()
        raiz.update()
        tercera = app._abrir_ayuda(ayuda_gui.PESTANA_CSV)
        obs["cerrada_abre_otra"] = tercera is not primera
        obs["ok"] = True
    except Exception as exc:                      # se reporta, no se traga
        obs["ok"] = False
        obs["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        try:
            raiz.destroy()
        except Exception:
            pass
    destino.write_text(json.dumps(obs, ensure_ascii=False), encoding="utf-8")
    return 0 if obs.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
