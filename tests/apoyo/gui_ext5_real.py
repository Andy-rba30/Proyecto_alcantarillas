"""
tests/apoyo/gui_ext5_real.py
============================
La aceptacion de EXT-5 SOBRE LA VENTANA DE VERDAD, para que
`tests/test_ext5_forma_gui.py` la lance en un proceso aparte:

    python -m tests.apoyo.gui_ext5_real <directorio de salida>

Que mide, y por que en una ventana real
---------------------------------------
Tres cosas que ningun test con el doble de tkinter puede ver, porque las tres
son el ESTADO de un widget despues de un gesto:

1. **El bloqueo real de C-01** despues de declarar los SIETE criterios del
   cajon POR EL CAMINO DEL RATON (el campo de la pestaña 2, su interprete y
   el boton «Aplicar solo a esta corrida»). Hasta EXT-5 el test de ventana
   real afirmaba que C-01 no dimensionaba y era CIEGO a por que: con '1'
   leido como 1.0 el marco no pasaba de M2 (`isinstance(int)` para
   `n_celdas_cajon`), y con '1' leido como 1 tampoco dimensiona --- le falta
   `S_cauce` en el CSV de perfil ---, de modo que la asercion pasaba igual.
   Aqui se vuelca la lista entera de bloqueos de C-01 y el `repr` de lo que
   quedo declarado, para que el test afirme CUAL es el bloqueo (PC-13).

2. **La cara de solo lectura de un criterio `Derivada` en la pestaña 2**:
   el estado real de los dos botones que escriben y del campo de valor, con
   el motivo que el tooltip lleva, al seleccionar
   `tabla_recubrimiento_aashto_mm` (EXT-V-04, la mitad de la pestaña 2 que
   EXT-1 dejo en la guardia del nucleo).

3. **El veredicto de 'nan' al escribir y al declarar** en la ventana
   emergente de un criterio de cara RANGO (`v_max_concreto_eleccion`): el
   color con que el campo se pinta al teclear, y el rotulo de estado tras
   pulsar «Declarar para esta corrida» (PC-14, segunda mitad).

Los datos del corredor, el CSV de perfil y las siete cadenas tecleadas son
los de `tests/apoyo/gui_corrida_perfil.py`: la corrida de aqui y la de alli
tienen que partir de la misma entrada, o comparar sus salidas no significaria
nada.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

import cli                                             # noqa: E402
from src import criterios_adoptados as ca
from tests.apoyo.gui_corrida_perfil import (           # noqa: E402
    CAJON_TECLEADO, CSV_PERFIL, EXTERNOS)

CLAVE_DERIVADA = "tabla_recubrimiento_aashto_mm"
CLAVE_DE_RANGO = "v_max_concreto_eleccion"
TEXTO_NO_NUMERO = "nan"


def _estado_boton(boton):
    return {"state": str(boton.boton.cget("state")),
            "tooltip": boton.tooltip.texto}


def main(salida: Path) -> int:
    import ttkbootstrap as tb

    import gui.app as gapp
    import gui.ventana_normativa as gvn

    salida.mkdir(parents=True, exist_ok=True)
    externos = salida / "datos_externos.json"
    externos.write_text(json.dumps(EXTERNOS, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    raiz = tb.Window(themename="litera")
    try:
        ventana = gapp.ExpedienteApp(raiz)
        ventana.csv_var.set(str(CSV_PERFIL))
        ventana.datos_externos_var.set(str(externos))
        ventana.proyecto_var.set("aceptacion EXT-5")
        ventana.alcance_var.set(cli.ALCANCE_PERFIL)
        raiz.update()

        # 1. Los siete del cajon, por el campo de la pestaña 2.
        declarados = {}
        rechazos = {}
        for clave, tecleado in CAJON_TECLEADO.items():
            ventana._clave_criterio_seleccionado = clave
            ventana.valor_declarado_var.set(tecleado)
            ventana._aplicar_valor_corrida()
            raiz.update()
            estado = ventana.lbl_estado_criterio.cget("text")
            if estado.startswith("Error:"):
                rechazos[clave] = estado
            else:
                declarados[clave] = repr(ca.valor(clave))

        ventana.ejecutar_pipeline()
        raiz.update()
        informe = ventana.informe
        if informe is None:
            print("ERROR: la GUI no produjo informe")
            return 1
        c01 = next(p for p in informe.puntos if p.punto.id == "C-01")
        bloqueos_c01 = [
            {"tipo": str(b.tipo.value), "etapa": b.etapa,
             "criterio": b.criterio, "diferido": b.diferido_por_alcance,
             "mensaje": b.mensaje}
            for b in c01.bloqueos]

        # 2. La cara de la pestaña 2 ante un criterio Derivada. La tabla
        # esta filtrada por alcance y el derivado es de expediente: se
        # ensancha el filtro para que la fila exista antes de seleccionarla.
        ventana.alcance_var.set(cli.ALCANCE_EXPEDIENTE)
        raiz.update()
        ventana.tree_criterios_todos.selection_set(CLAVE_DERIVADA)
        ventana._al_seleccionar_criterio()
        raiz.update()
        cara_derivada = {
            "aplicar": _estado_boton(ventana.btn_aplicar_corrida),
            "guardar": _estado_boton(ventana.btn_guardar_archivo),
            "ventana_norma": _estado_boton(ventana.btn_ventana_norma),
            "campo": str(ventana.ent_valor_declarado.cget("state")),
        }
        # ...y que un criterio corriente devuelve la cara editable.
        ventana.tree_criterios_todos.selection_set("talud_terraplen")
        ventana._al_seleccionar_criterio()
        raiz.update()
        cara_corriente = {
            "aplicar": _estado_boton(ventana.btn_aplicar_corrida),
            "guardar": _estado_boton(ventana.btn_guardar_archivo),
            "campo": str(ventana.ent_valor_declarado.cget("state")),
        }

        # 3. 'nan' en la emergente de un criterio de cara RANGO.
        emergente = gvn.VentanaNormativa(raiz, CLAVE_DE_RANGO)
        raiz.update()
        emergente.valor_var.set(TEXTO_NO_NUMERO)
        raiz.update()
        al_escribir = {"color": emergente.campo.color,
                       "mensaje": emergente.lbl_validacion.cget("text")}
        emergente._declarar()
        raiz.update()
        al_declarar = {"estado": emergente.lbl_estado.cget("text"),
                       "declarado": ca.declarado_en_caliente(CLAVE_DE_RANGO)}
        emergente.destroy()

        resumen = {
            "cajon_declarado": declarados,
            "cajon_rechazado": rechazos,
            "c01_dimensionado": c01.dimensionado,
            "bloqueos_c01": bloqueos_c01,
            "dimensionados": sorted(p.punto.id for p in informe.puntos
                                    if p.dimensionado),
            "cara_derivada": cara_derivada,
            "cara_corriente": cara_corriente,
            "nan_al_escribir": al_escribir,
            "nan_al_declarar": al_declarar,
            "color_error": gvn.COLOR_ERROR,
        }
    finally:
        raiz.destroy()

    (salida / "resumen_ext5.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[3])
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
