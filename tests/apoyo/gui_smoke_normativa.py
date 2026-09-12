"""
tests/apoyo/gui_smoke_normativa.py
==================================
El SMOKE de construccion de widgets que la ficha SIS-F-01 pedia y ningun otro
apoyo daba, para que `tests/test_gui_contrato.py` lo lance en un proceso
aparte.

    python -m tests.apoyo.gui_smoke_normativa <archivo de salida .json>

Que hueco cubre, dicho contra los otros dos apoyos
--------------------------------------------------
`gui_corrida_perfil.py` construye la aplicacion y corre el pipeline de
perfil; `gui_seleccion_real.py` ejercita la seleccion de la pestana 2. Entre
los dos, `gui/ventana_normativa.py` -- el archivo entero -- seguia sin
construirse NUNCA bajo un `Tk` real: `_tras_declarar_en_ventana` se llama
directo (y esta escrito ahi por que), y `tests/test_ventana_normativa.py`
compara el CONTENIDO sin pantalla. Un `grid` mal puesto, un atributo mal
escrito o un `iid` repetido en cualquiera de los siete `_bloque_*` de la
emergente revienta al abrirla y ningun test lo veia. Este apoyo hace lo que
el proyectista hace: construye la aplicacion, puebla las cuatro pestanas con
`tests/ejemplo_puntos.csv` (el CSV de EXPEDIENTE; el otro apoyo ya cubre el
de perfil), y abre y cierra la ventana normativa de un criterio `de_tabla`.

Por que es un modulo y no un test: la misma razon de los otros dos apoyos --
`test_gui_contrato.py` instala dobles de tkinter que no se pueden retirar, y
con ellos la ventana seria un espejismo --.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for _ruta in (str(RAIZ), str(RAIZ / "src")):
    if _ruta not in sys.path:
        sys.path.insert(0, _ruta)

CSV_EXPEDIENTE = RAIZ / "tests" / "ejemplo_puntos.csv"

# La MISMA clave que el test de punta a punta de `test_gui_contrato.py`
# declara desde la ventana: es `de_tabla` (Tabla C.2 del HDS-5) y por eso su
# emergente pinta la cara TABLA entera, que es la mas densa de las cuatro.
CRITERIO_DE_TABLA = "ke_entrada"

# Los mismos datos externos del test de punta a punta, tecleados como los
# teclea el proyectista (los campos de la pestana 1, no un JSON).
TECLEADO_EXTERNO = {"luz_m": "2.0", "TW_m": "0.0", "longitud_m": "14.0"}


def main(destino: Path) -> int:
    import tkinter as tk

    import ttkbootstrap as tb

    import gui.app as gapp

    raiz = tb.Window(themename="litera")
    obs = {}
    try:
        ventana = gapp.ExpedienteApp(raiz)
        obs["pestanas"] = len(ventana.nb.tabs())

        # 1. Poblar la pestana 1 como el proyectista: CSV y campos externos.
        ventana.csv_var.set(str(CSV_EXPEDIENTE))
        for campo, texto in TECLEADO_EXTERNO.items():
            ventana.externos_vars[campo].set(texto)
        ventana.proyecto_var.set("smoke de la ventana normativa")
        raiz.update()

        # 2. Correr. Con `ke_entrada` sin declarar el punto se BLOQUEA, no
        #    revienta: lo que se puebla es el tablero de pendientes, que es
        #    exactamente lo que la pantalla tiene que saber pintar.
        ventana.ejecutar_pipeline()
        raiz.update()
        obs["informe"] = ventana.informe is not None
        obs["puntos_en_tabla"] = len(ventana.tree_puntos.get_children())

        # 3. Las CUATRO pestanas se seleccionan y repintan de verdad.
        for pestana in (ventana.tab_datos, ventana.tab_criterios,
                        ventana.tab_puntos, ventana.tab_resumen):
            ventana.nb.select(pestana)
            raiz.update()
        obs["pestanas_recorridas"] = True

        # 4. La ventana normativa del criterio `de_tabla`, abierta POR EL
        #    CAMINO DEL RATON: seleccion real en el arbol (el evento se
        #    encola y el `update()` lo procesa) y el mismo metodo que cuelga
        #    del boton y del doble clic.
        ventana.nb.select(ventana.tab_criterios)
        ventana.tree_criterios_todos.selection_set(CRITERIO_DE_TABLA)
        raiz.update()
        obs["seleccionado"] = ventana._clave_criterio_seleccionado

        ventana._abrir_ventana_normativa()
        raiz.update()
        emergentes = [w for w in raiz.winfo_children()
                      if isinstance(w, tk.Toplevel)]
        obs["emergentes_abiertas"] = len(emergentes)
        if emergentes:
            emergente = emergentes[0]
            obs["titulo_emergente"] = emergente.title()
            obs["widgets_de_la_emergente"] = sum(
                1 for _ in _descendientes(emergente))
            # 5. Y se CIERRA como la cierra el usuario.
            emergente.destroy()
            raiz.update()
        obs["emergentes_tras_cerrar"] = sum(
            1 for w in raiz.winfo_children() if isinstance(w, tk.Toplevel))
    finally:
        raiz.destroy()

    destino.write_text(json.dumps(obs, ensure_ascii=False, indent=2),
                       encoding="utf-8")
    print(json.dumps(obs, ensure_ascii=False))
    return 0


def _descendientes(widget):
    for hijo in widget.winfo_children():
        yield hijo
        yield from _descendientes(hijo)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[3])
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
