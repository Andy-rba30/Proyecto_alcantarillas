"""
tests/apoyo/gui_eb_real.py
==========================
La aceptacion de E-B SOBRE LA VENTANA DE VERDAD, para que
`tests/test_eb_editores_comparador.py` la lance en un proceso aparte:

    python -m tests.apoyo.gui_eb_real <directorio de salida>

Que mide, y por que en una ventana real
---------------------------------------
Los editores tipados (E10) son WIDGETS: lo que se afirma de ellos es el
estado de un campo despues de un gesto --- el color con que se pinta al
teclear un numero fuera de la ventana, la lista de pares tras pulsar
«Añadir par», el valor que aparece al elegir una fila del desplegable ---,
y eso no lo ve el doble de tkinter. Aqui se hacen los gestos por el mismo
camino del raton (las variables de los campos, los botones, la seleccion
del desplegable) y se vuelca lo que quedo:

1. `secciones_cajon_normalizadas` (serie de pares): tres pares por el editor,
   «Aplicar», y lo que `criterios_adoptados` tiene declarado con su
   procedencia. El literal de la pestaña lo compuso el editor.
2. `seccion_receptor` (dict con ventana por campo): `n` = 0.05 se pinta en
   rojo al escribir y «Aplicar» no declara NADA (atomico); con `n` = 0.030
   entra el dict entero.
3. `ke_entrada` (float de tabla): elegir la fila de la Tabla C.2 pone la
   celda (0.5) y la procedencia la nombra; teclear 0.55 sin nota no entra
   (DIFIERE de la celda); con nota entra y la procedencia dice DIFIERE.
4. Las dos columnas nuevas (responsable, evidencia) en el tablero de la
   pestaña 4 tras correr y en el anticipo de la pestaña 1 (E13 reducido).
5. La comparacion de la corrida con su propio volcado (E14): iguales.

Los datos del corredor y el CSV de perfil son los de
`tests/apoyo/gui_corrida_perfil.py`.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

import cli                                             # noqa: E402
from src import criterios_adoptados as ca
from src import declaracion as dec
from src import sesion as ses
from tests.apoyo.gui_corrida_perfil import CSV_PERFIL, EXTERNOS  # noqa: E402

SERIE = "secciones_cajon_normalizadas"
RECEPTOR = "seccion_receptor"
KE = "ke_entrada"
KE_FILA = "concreto_headwall_square_edge"

PARES_TECLEADOS = (("1,20", "0.90"), ("1.50", "1,20"), ("2.00", "1.50"))


def _seleccionar(ventana, raiz, clave):
    ventana._clave_criterio_seleccionado = clave
    ventana._llenar_tabla_criterios()
    ventana.tree_criterios_todos.selection_set(clave)
    ventana._al_seleccionar_criterio()
    raiz.update()
    return ventana.editor


def main(salida: Path) -> int:
    import ttkbootstrap as tb

    import gui.app as gapp

    salida.mkdir(parents=True, exist_ok=True)
    externos = salida / "datos_externos.json"
    externos.write_text(json.dumps(EXTERNOS, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    resumen = {}

    raiz = tb.Window(themename="litera")
    try:
        ventana = gapp.ExpedienteApp(raiz)
        ventana.csv_var.set(str(CSV_PERFIL))
        ventana.datos_externos_var.set(str(externos))
        ventana.proyecto_var.set("aceptacion E-B")
        ventana.alcance_var.set(cli.ALCANCE_PERFIL)
        raiz.update()

        # 1. La serie de pares, par a par.
        editor = _seleccionar(ventana, raiz, SERIE)
        for a, b in PARES_TECLEADOS:
            editor.vars["primero"].set(a)
            editor.vars["segundo"].set(b)
            editor._anadir_fila()
            raiz.update()
        literal = ventana.valor_declarado_var.get()
        tipo_de_editor = editor.esquema.tipo_de_editor
        # Declarar repinta la tabla y REMONTA el editor con el valor
        # declarado (es lo que el proyectista ve): la referencia de arriba
        # queda desmontada y no se vuelve a usar.
        ventana._aplicar_valor_corrida()
        raiz.update()
        p = dec.procedencia_de(SERIE)
        resumen["serie"] = {
            "tipo_de_editor": tipo_de_editor,
            "literal": literal,
            "estado": ventana.lbl_estado_criterio.cget("text"),
            "declarado": ca.valor(SERIE) if ca.declarado_en_caliente(SERIE) else None,
            "procedencia_modo": p.modo if p else None,
        }

        # 2. El dict del receptor: un campo fuera de ventana.
        editor = _seleccionar(ventana, raiz, RECEPTOR)
        editor.vars["n"].set("0.05")
        raiz.update()
        color_fuera = editor.colores()["n"]
        ventana._aplicar_valor_corrida()
        raiz.update()
        rechazado = ventana.lbl_estado_criterio.cget("text")
        declarado_tras_rechazo = ca.declarado_en_caliente(RECEPTOR)
        editor = ventana.editor        # el rechazo no remonta; se relee igual
        editor.vars["n"].set("0,030")
        raiz.update()
        ventana._aplicar_valor_corrida()
        raiz.update()
        resumen["receptor"] = {
            "color_n_fuera": color_fuera,
            "rechazado": rechazado,
            "declarado_tras_rechazo": declarado_tras_rechazo,
            "estado_final": ventana.lbl_estado_criterio.cget("text"),
            "declarado": ca.valor(RECEPTOR) if ca.declarado_en_caliente(RECEPTOR) else None,
        }

        # 3. ke_entrada: la fila de la tabla, y una adopcion distinta.
        editor = _seleccionar(ventana, raiz, KE)
        editor.elegir_fila(KE_FILA)
        raiz.update()
        valor_tras_fila = ventana.valor_declarado_var.get()
        ventana._aplicar_valor_corrida()
        raiz.update()
        p = dec.procedencia_de(KE)
        procedencia_fila = list(p.filas) if p else None
        fila_elegida = editor.fila()
        editor = ventana.editor        # remontado tras declarar
        editor.elegir_fila(KE_FILA)
        editor.var_valor.set("0.55")
        raiz.update()
        ventana._aplicar_valor_corrida()
        raiz.update()
        rechazo_sin_nota = ventana.lbl_estado_criterio.cget("text")
        editor = ventana.editor
        editor.elegir_fila(KE_FILA)
        editor.var_valor.set("0.55")
        editor.nota_var.set("embocadura intermedia medida en obra")
        raiz.update()
        ventana._aplicar_valor_corrida()
        raiz.update()
        p = dec.procedencia_de(KE)
        resumen["ke"] = {
            "valor_tras_elegir_fila": float(valor_tras_fila),
            "fila_elegida": fila_elegida,
            "procedencia_fila": procedencia_fila,
            "rechazo_sin_nota": rechazo_sin_nota,
            "estado_con_nota": ventana.lbl_estado_criterio.cget("text"),
            "difiere_con_nota": bool(p and p.difiere_de_la_celda()),
            "declarado": ca.valor(KE) if ca.declarado_en_caliente(KE) else None,
        }

        # 4. Correr, y las dos columnas nuevas.
        ventana.ejecutar_pipeline()
        raiz.update()
        if ventana.informe is None:
            print("ERROR: la GUI no produjo informe")
            return 1
        columnas_4 = list(ventana.tree_criterios["columns"])
        filas_4 = [ventana.tree_criterios.item(i)["values"]
                   for i in ventana.tree_criterios.get_children()]
        i_resp = columnas_4.index("responsable")
        resumen["columnas_pestana_4"] = columnas_4
        resumen["bloqueantes_con_responsable"] = sum(
            1 for f in filas_4 if str(f[i_resp]).strip())
        resumen["filas_pestana_4"] = len(filas_4)
        resumen["columnas_anticipo"] = list(ventana.tree_anticipo["columns"])
        resumen["anticipo_con_responsable"] = sum(
            1 for i in ventana.tree_anticipo.get_children()
            if str(ventana.tree_anticipo.item(i)["values"][2]).strip())

        # 5. Comparar la corrida con su propio volcado.
        propio = salida / "propio.informe.json"
        ses.escribir_json_atomico(propio, ventana.volcado_de_la_corrida)
        resultado = ventana.comparar_informe(str(propio))
        raiz.update()
        resumen["comparacion"] = {
            "iguales": bool(resultado and resultado.iguales),
            "lineas": list(resultado.lineas()) if resultado else [],
        }
    finally:
        raiz.destroy()

    (salida / "resumen_eb.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
