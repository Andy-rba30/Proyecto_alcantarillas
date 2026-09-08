"""
tests/apoyo/gui_seleccion_real.py
=================================
La SELECCION de la tabla de criterios, ejercitada sobre una ventana de verdad,
para que `tests/test_gui_contrato.py` la lance en un proceso aparte.

    python -m tests.apoyo.gui_seleccion_real <archivo de salida .json>

Por que hace falta, dicho con el defecto que se escapo
------------------------------------------------------
La suite estuvo VERDE con tres defectos dentro, y no por casualidad:
`gui_corrida_perfil.py` --- el otro apoyo, el de la corrida de punta a punta ---
asigna `ventana._clave_criterio_seleccionado` A MANO y no toca ni el filtro ni
la seleccion real del `Treeview`. Con eso se prueba lo que la ventana DECIDE y
no lo que el usuario HACE, y los tres defectos vivian justo en medio:

  - `<<TreeviewSelect>>` no es sincrono: Tk lo ENCOLA. `_llenar_tabla_criterios`
    borraba todas las filas y no reponia la seleccion, de modo que en el
    siguiente giro del bucle de eventos `_al_seleccionar_criterio` entraba con
    seleccion vacia y ponia `_clave_criterio_seleccionado = None`.
  - Teclear en «Buscar» deseleccionaba el criterio: detalle en blanco, botones
    apagados y el mensaje de confirmacion borrado.
  - Y `_tras_declarar_en_ventana` --- el callback con que la ventana normativa
    avisa de que se declaro --- hacia `selection_set` sobre una fila que el
    filtro habia excluido: `_tkinter.TclError`, que NO desciende de
    `ErrorProyecto` y por tanto la GUI no puede distinguir de un fallo del
    programa.

Nada de eso se ve sin un `Tk` real: hace falta que el evento se ENCOLE y que el
bucle lo procese. Por eso este modulo existe y por eso corre aparte, igual que
`gui_corrida_perfil.py` y por la misma razon --- `test_gui_contrato.py` instala
dobles de tkinter que ya no se pueden retirar ---.

Que se ejercita y que no
------------------------
Se ejercita el CAMINO DEL RATON: `selection_set` sobre el arbol (que dispara el
evento de verdad), escritura en las variables del filtro (que dispara la traza
de verdad) y `raiz.update()` entre medias para que el bucle procese lo encolado.
Sin ese `update()` el defecto no aparece, que es precisamente lo que lo hacia
invisible.

`_tras_declarar_en_ventana` se llama directamente y no abriendo la emergente:
es el CONTRATO entre las dos ventanas --- `_abrir_ventana_normativa` se lo pasa
como `al_declarar` --- y es donde reventaba. Abrir la emergente de verdad
probaria la emergente, que no es lo que aqui se prueba.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for _ruta in (str(RAIZ), str(RAIZ / "src")):
    if _ruta not in sys.path:
        sys.path.insert(0, _ruta)

import criterios_adoptados as ca                       # noqa: E402

# Un texto que no casa con ninguna clave ni concepto: el filtro deja fuera a
# todo el archivo, que es el caso extremo y el que hace visible el defecto.
SIN_COINCIDENCIAS = "zzzz-no-casa-con-nada"


def _clave_pendiente():
    """Una clave PENDIENTE cualquiera, tomada del archivo y no escrita aqui."""
    return sorted(c for c, v in ca.CRITERIOS.items() if v.valor is None)[0]


def main(destino: Path) -> int:
    import ttkbootstrap as tb

    import gui.app as gapp

    raiz = tb.Window(themename="litera")
    obs = {}
    try:
        ventana = gapp.ExpedienteApp(raiz)
        ventana.nb.select(ventana.tab_criterios)
        raiz.update()

        clave = _clave_pendiente()
        obs["clave"] = clave

        # 1. Seleccion REAL: se dispara `<<TreeviewSelect>>` de verdad.
        ventana.tree_criterios_todos.selection_set(clave)
        raiz.update()
        obs["seleccionada_al_empezar"] = ventana._clave_criterio_seleccionado
        obs["detalle_al_empezar"] = bool(
            ventana.txt_detalle_criterio.get("1.0", "end").strip())
        obs["boton_norma_al_empezar"] = str(ventana.btn_ventana_norma.cget("state"))

        # 2. Declarar por el camino de la pestana, y que la confirmacion quede.
        ventana.valor_declarado_var.set("1.5")
        ventana._aplicar_valor_corrida()
        raiz.update()
        obs["confirmacion_tras_declarar"] = ventana.lbl_estado_criterio.cget("text")

        # 3. TECLEAR EN EL FILTRO no puede perder la seleccion.
        ventana.filtro_texto_var.set(SIN_COINCIDENCIAS)
        raiz.update()
        obs["seleccionada_tras_teclear"] = ventana._clave_criterio_seleccionado
        obs["seleccion_del_arbol"] = list(ventana.tree_criterios_todos.selection())
        obs["detalle_tras_teclear"] = bool(
            ventana.txt_detalle_criterio.get("1.0", "end").strip())
        obs["boton_norma_tras_teclear"] = str(ventana.btn_ventana_norma.cget("state"))
        obs["confirmacion_tras_teclear"] = ventana.lbl_estado_criterio.cget("text")

        # 4. SEGUNDO TECLEO: la fila protegida sigue ahi. Es el caso que la
        #    primera version fallaba --- protegia UN refiltrado y no el
        #    siguiente ---, y por eso se teclea dos veces y no una.
        ventana.filtro_texto_var.set(SIN_COINCIDENCIAS + "-mas")
        raiz.update()
        obs["fila_tras_segundo_tecleo"] = (
            clave in ventana.tree_criterios_todos.get_children())
        obs["seleccionada_tras_segundo_tecleo"] = ventana._clave_criterio_seleccionado

        # 5. DECLARAR DESDE LA EMERGENTE con el filtro puesto. La emergente no
        #    es modal, de modo que entre abrirla y declarar se pudo filtrar.
        try:
            ventana._tras_declarar_en_ventana(clave)
            raiz.update()
            obs["declarar_con_filtro"] = "ok"
        except Exception as exc:
            obs["declarar_con_filtro"] = f"{type(exc).__name__}: {exc}"
        obs["fila_tras_declarar_desde_emergente"] = (
            clave in ventana.tree_criterios_todos.get_children())

        # 6. Y el caso peor: la emergente declara una clave que NO es la
        #    seleccionada, porque el usuario movio la seleccion por debajo.
        ventana.filtro_texto_var.set("")
        raiz.update()
        otra = sorted(c for c in ca.CRITERIOS if c != clave)[0]
        ventana.tree_criterios_todos.selection_set(otra)
        raiz.update()
        ventana.filtro_texto_var.set(SIN_COINCIDENCIAS)
        raiz.update()
        try:
            ventana._tras_declarar_en_ventana(clave)
            raiz.update()
            obs["declarar_otra_clave"] = "ok"
        except Exception as exc:
            obs["declarar_otra_clave"] = f"{type(exc).__name__}: {exc}"
    finally:
        raiz.destroy()

    destino.write_text(json.dumps(obs, ensure_ascii=False, indent=2),
                       encoding="utf-8")
    print(json.dumps(obs, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[3])
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
