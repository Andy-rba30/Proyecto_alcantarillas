"""
tests/apoyo/gui_capturas.py
===========================
Capturas de pantalla de las CUATRO pestañas de la ventana principal, sobre
una ventana de verdad, para comparar el antes y el despues de cada bloque
del rediseño visual.

    xvfb-run -a -s "-screen 0 1400x1100x24" python3.12 -m tests.apoyo.gui_capturas <directorio>

Que hace
--------
Construye la aplicacion como la construye `gui.app.main` --- `tb.Window` con
el tema de arranque; el tema propio de la interfaz lo aplica la propia
ventana ---, la puebla con `tests/ejemplo_puntos.csv` y los tres datos
externos que el smoke de la ventana normativa teclea, EJECUTA el pipeline
(para que las pestañas 3 y 4 muestren una corrida real y no una tabla
vacia), selecciona un punto y un criterio (para que los paneles de detalle
tengan contenido), y guarda un PNG por pestaña:

    pestana_1_datos.png, pestana_2_criterios.png,
    pestana_3_resultados.png, pestana_4_resumen.png

Todo lo que se ve en las capturas lo produce el programa: ningun rotulo ni
valor de ejemplo se escribe aqui. Lo unico que este apoyo decide es QUE
pestaña se muestra y que fila esta seleccionada.

Por que es un modulo y no un test: la misma razon de los otros apoyos de
`tests/apoyo/gui_*.py`. No es parte de la suite: es una herramienta de
revision visual, y la captura la hace `PIL.ImageGrab`, que es dependencia
de weasyprint (Pillow) y no del calculo.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

CSV_EXPEDIENTE = RAIZ / "tests" / "ejemplo_puntos.csv"

# Los mismos datos externos del smoke de la ventana normativa
# (`tests/apoyo/gui_smoke_normativa.py`), tecleados como los teclea el
# proyectista en la pestaña 1.
TECLEADO_EXTERNO = {"luz_m": "2.0", "TW_m": "0.0", "longitud_m": "14.0"}

# El criterio que se selecciona en la pestaña 2 para que el panel de detalle
# tenga contenido: es `de_tabla` (Tabla C.2 del HDS-5), el mismo del smoke.
CRITERIO_SELECCIONADO = "ke_entrada"

GEOMETRIA = "1280x1000+0+0"


def _capturar(raiz, destino: Path):
    from PIL import ImageGrab

    raiz.update_idletasks()
    raiz.update()
    x, y = raiz.winfo_rootx(), raiz.winfo_rooty()
    w, h = raiz.winfo_width(), raiz.winfo_height()
    imagen = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    imagen.save(destino)
    return destino


def main(salida: Path) -> int:
    import ttkbootstrap as tb

    import gui.app as gapp

    salida.mkdir(parents=True, exist_ok=True)
    raiz = tb.Window(themename="litera")
    raiz.geometry(GEOMETRIA)
    escritas = []
    try:
        ventana = gapp.ExpedienteApp(raiz)
        raiz.geometry(GEOMETRIA)
        ventana.csv_var.set(str(CSV_EXPEDIENTE))
        for campo, texto in TECLEADO_EXTERNO.items():
            ventana.externos_vars[campo].set(texto)
        ventana.proyecto_var.set("capturas del rediseño visual")
        raiz.update()

        ventana.ejecutar_pipeline()
        raiz.update()

        # Pestaña 2 con un criterio seleccionado, pestaña 3 con el primer
        # punto seleccionado: los paneles de detalle se ven con contenido.
        ventana.tree_criterios_todos.selection_set(CRITERIO_SELECCIONADO)
        ventana.tree_criterios_todos.see(CRITERIO_SELECCIONADO)
        puntos = ventana.tree_puntos.get_children()
        if puntos:
            ventana.tree_puntos.selection_set(puntos[0])
        raiz.update()

        pestanas = (
            ("pestana_1_datos.png", ventana.tab_datos),
            ("pestana_2_criterios.png", ventana.tab_criterios),
            ("pestana_3_resultados.png", ventana.tab_puntos),
            ("pestana_4_resumen.png", ventana.tab_resumen),
        )
        for nombre, pestana in pestanas:
            ventana.nb.select(pestana)
            raiz.update()
            escritas.append(_capturar(raiz, salida / nombre))
    finally:
        raiz.destroy()

    for ruta in escritas:
        print(ruta)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[3])
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
