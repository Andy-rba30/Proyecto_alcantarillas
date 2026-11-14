"""
tests/apoyo/gui_ui2_pestana4_real.py
====================================
UI-2 SOBRE LA VENTANA DE VERDAD: la pestaña 4 con la memoria resumida (ficha
T12-04) y el panel «Cabezal del proyecto» (hueco 3 del §0 de la cadena de
interfaz).

    python -m tests.apoyo.gui_ui2_pestana4_real <directorio de salida>

Corre en un proceso limpio por la misma razon que `gui_ext8_real.py`:
`test_gui_contrato.py` instala dobles de `tkinter` y con ellos la ventana
seria un espejismo. Y en un proceso limpio no hay declaraciones de la suite
(`conftest.py`): la corrida es la de referencia `expediente_cabezal` de
`src/indice_formulas.CORRIDAS_DE_REFERENCIA` tal como `correr_referencia` la
hace --- su CSV, sus externos, su `sitio.json` y sus declaraciones, con
DATOS DE PRUEBA ---, tecleada en los campos de la pestaña 1.

Que se mide, en orden:

  1. recien abierta, los SIETE botones del grupo de exportacion apagados con
     `MOTIVO_SIN_CORRIDA` y el panel del cabezal vacio con su motivo;
  2. tras correr, los siete encendidos y el panel con el texto que la CLI
     imprime del cabezal del proyecto (`cli._lineas_cabezal`);
  3. la memoria completa y la RESUMIDA en HTML, escritas por los dos
     botones (las dos se guardan para que el test compare su encabezado de
     trazabilidad);
  4. la resumida en PDF: si weasyprint esta operativo en ESTE interprete,
     por el proceso hijo de EXT-8 --- los dos botones de PDF apagados con
     `MOTIVO_EXPORTANDO_PDF`, «Cancelar PDF» encendido, el rotulo de
     progreso, el estado terminal y el JSON del hijo guardado antes de que
     el directorio de trabajo se retire ---, y despues una segunda
     exportacion cancelada; si no, por el navegador en este proceso;
  4b. la corrida de referencia CON hidrologia (`hidrologia_calculada`, con
     los dos CSV en sus campos) y su resumida en PDF por el hijo: la sesion
     que el hijo recibe lleva las dos rutas y su JSON es el de la ventana
     (revision de UI-2);
  5. un gesto que invalida (escribir en el campo del CSV de cuencas): los
     siete apagados con su motivo y el panel vacio con el mismo;
  6. la corrida de PERFIL de la guia (`perfil_guia`): el panel dice lo que
     la CLI imprime cuando la Fase 9 se difiere;
  7. una corrida que falla: el panel y los siete dicen que no hubo informe.
"""

import json
import shutil
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

import cli                                             # noqa: E402
from src import criterios_adoptados as ca              # noqa: E402
from src import indice_formulas as ind                 # noqa: E402

LIMITE_ESPERA_S = 300.0


def corrida(nombre):
    return next(c for c in ind.CORRIDAS_DE_REFERENCIA if c.nombre == nombre)


def _exportadores(ventana):
    import gui.app as gapp
    return {nombre.removeprefix("btn_"): {
        "encendido": str(getattr(ventana, nombre).cget("state")) == "normal",
        "motivo": getattr(ventana, nombre).motivo}
        for nombre in gapp.BOTONES_DE_EXPORTACION}


def _panel(ventana):
    return {"texto": ventana.txt_cabezal.get("1.0", "end-1c"),
            "motivo": ventana.lbl_cabezal.cget("text")}


def _ruta(ruta):
    return "" if ruta is None else str(ruta)


def _poner_corrida(ventana, referencia):
    """Los campos de la pestaña 1 y las declaraciones, como `correr_referencia`."""
    ventana.cuencas_var.set(_ruta(referencia.cuencas))
    ventana.estacion_var.set(_ruta(referencia.estacion))
    ventana.csv_var.set(str(referencia.csv))
    ventana.datos_externos_var.set(str(referencia.externos))
    ventana.datos_sitio_var.set(_ruta(referencia.sitio))
    ventana.alcance_var.set(referencia.alcance)
    for clave in list(ca.valores_dinamicos()):
        ca.quitar_valor_dinamico(clave)
    for clave, valor in referencia.declaraciones.items():
        ca.establecer_valor_dinamico(clave, valor)


def _correr(ventana, raiz):
    ventana.ejecutar_pipeline()
    raiz.update()
    return ventana.informe


def _esperar_pdf(ventana, raiz):
    inicio = time.monotonic()
    while ventana.proceso_pdf is not None and not ventana.proceso_pdf.estado.terminal:
        raiz.update()
        time.sleep(0.05)
        if time.monotonic() - inicio > LIMITE_ESPERA_S:
            return False
    for _ in range(10):
        raiz.update()
        time.sleep(0.05)
    return True


def main(salida: Path) -> int:
    import ttkbootstrap as tb
    import webbrowser

    import gui.app as gapp
    from src.modulos import M11_reporte as M11

    salida.mkdir(parents=True, exist_ok=True)
    dialogos = []
    gapp.messagebox.showinfo = lambda titulo, texto, *a, **k: dialogos.append(
        ("info", titulo, texto))
    gapp.messagebox.showerror = lambda titulo, texto, *a, **k: dialogos.append(
        ("error", titulo, texto))
    gapp.messagebox.askyesno = lambda *a, **k: True
    webbrowser.open = lambda *a, **k: True
    # El JSON y la sesion del hijo se guardan ANTES de que `_terminar_pdf`
    # retire el directorio de trabajo: es lo que dice que el hijo corrio la
    # misma obra. `prefijo` nombra la exportacion en curso.
    limpiar = gapp.expdf.ProcesoPdf.limpiar
    prefijo = {"valor": "hijo_resumida"}

    def _limpiar_guardando(proceso):
        for origen, sufijo in ((proceso.ruta_json, ".json"),
                               (proceso.ruta_sesion, ".sesion.json")):
            if origen.is_file():
                shutil.copy(origen, salida / f"{prefijo['valor']}{sufijo}")
        limpiar(proceso)

    gapp.expdf.ProcesoPdf.limpiar = _limpiar_guardando

    raiz = tb.Window(themename="litera")
    r = {"motivo_sin_corrida": gapp.MOTIVO_SIN_CORRIDA,
         "motivo_sin_corrida_cabezal": gapp.MOTIVO_SIN_CORRIDA_CABEZAL,
         "motivo_exportando_pdf": gapp.MOTIVO_EXPORTANDO_PDF,
         "motivo_hidrologia_cambiada": gapp.MOTIVO_HIDROLOGIA_CAMBIADA,
         "motivo_corrida_fallida": gapp.MOTIVO_CORRIDA_FALLIDA}
    try:
        ventana = gapp.ExpedienteApp(raiz)
        ventana.proyecto_var.set("DATOS DE PRUEBA - UI-2")
        raiz.update()

        # 1. Recien abierta.
        r["antes"] = {"exportadores": _exportadores(ventana),
                      "panel": _panel(ventana),
                      "rotulo": ventana.btn_json.rotulo.cget("text")}

        # 2. La corrida de referencia con cabezal.
        referencia = corrida("expediente_cabezal")
        _poner_corrida(ventana, referencia)
        informe = _correr(ventana, raiz)
        r["tras_correr"] = {
            "informe": informe is not None,
            "exportadores": _exportadores(ventana),
            "panel": _panel(ventana),
            "lineas_de_la_cli": [] if informe is None else cli._lineas_cabezal(informe.cabezal),
            "ayuda_pdf_resumida": ventana.btn_pdf_resumida.ayuda,
            "error_visible": ventana.lbl_error_datos.cget("text")}
        (salida / "ventana.json").write_text(
            json.dumps(ventana.volcado_de_la_corrida, ensure_ascii=False,
                       allow_nan=False, indent=1), encoding="utf-8")

        # 3. Las dos memorias en HTML, por sus botones.
        for nombre, metodo in (("completa.html", ventana.exportar_html),
                               ("resumida.html", ventana.exportar_html_resumida)):
            destino = salida / nombre
            gapp.filedialog.asksaveasfilename = lambda _d=destino, **kw: str(_d)
            metodo()
            raiz.update()

        # 4. La resumida en PDF.
        r["weasyprint_disponible"] = M11.weasyprint_disponible()
        destino = salida / "resumida_impresa.pdf"
        gapp.filedialog.asksaveasfilename = lambda **kw: str(destino)
        ventana.exportar_pdf_resumida()
        raiz.update()
        pdf = {}
        if r["weasyprint_disponible"]:
            pdf["comando"] = list(ventana.proceso_pdf.comando)
            pdf["durante"] = {
                "pdf_resumida": {"encendido": str(ventana.btn_pdf_resumida.cget("state")) == "normal",
                                 "motivo": ventana.btn_pdf_resumida.motivo},
                "pdf": {"encendido": str(ventana.btn_pdf.cget("state")) == "normal",
                        "motivo": ventana.btn_pdf.motivo},
                "cancelar": str(ventana.btn_cancelar_pdf.cget("state")) == "normal",
                "rotulo": ventana.lbl_estado_pdf.cget("text")}
            pdf["termino_a_tiempo"] = _esperar_pdf(ventana, raiz)
            pdf["estado_final"] = ventana.proceso_pdf.estado.value
            pdf["progreso_visto"] = list(ventana.proceso_pdf.progreso_visto)
            pdf["existe"] = destino.is_file() and destino.stat().st_size > 0
            pdf["cabecera"] = destino.read_bytes()[:4].decode("latin-1") if pdf["existe"] else ""
            pdf["despues"] = {
                "pdf_resumida": str(ventana.btn_pdf_resumida.cget("state")) == "normal",
                "pdf": str(ventana.btn_pdf.cget("state")) == "normal",
                "cancelar": str(ventana.btn_cancelar_pdf.cget("state")) == "normal"}
            pdf["rotulo_final"] = ventana.lbl_estado_pdf.cget("text")
            # Y cancelar: otra exportacion de la resumida, terminada a mano.
            cancelada = salida / "cancelada.pdf"
            gapp.filedialog.asksaveasfilename = lambda **kw: str(cancelada)
            prefijo["valor"] = "hijo_cancelado"
            ventana.exportar_pdf_resumida()
            raiz.update()
            ventana._cancelar_pdf()
            pdf["cancelacion_termino"] = _esperar_pdf(ventana, raiz)
            pdf["estado_cancelado"] = ventana.proceso_pdf.estado.value
            pdf["cancelada_no_existe"] = not cancelada.exists()
            pdf["rotulo_cancelado"] = ventana.lbl_estado_pdf.cget("text")
        else:
            pdf["html_navegador_existe"] = destino.with_suffix(".html").is_file()
            pdf["rotulo_final"] = ventana.lbl_estado_pdf.cget("text")
        r["pdf_resumida"] = pdf

        # 4b. La resumida en PDF de una corrida CON hidrologia.
        hidro = corrida("hidrologia_calculada")
        _poner_corrida(ventana, hidro)
        informe = _correr(ventana, raiz)
        h = {"informe": informe is not None,
             "con_hidrologia": informe is not None and informe.hidrologia is not None,
             "error_visible": ventana.lbl_error_datos.cget("text")}
        if informe is not None:
            (salida / "ventana_hidrologia.json").write_text(
                json.dumps(ventana.volcado_de_la_corrida, ensure_ascii=False,
                           allow_nan=False, indent=1), encoding="utf-8")
        if r["weasyprint_disponible"] and informe is not None:
            prefijo["valor"] = "hijo_hidrologia"
            destino_h = salida / "resumida_hidrologia.pdf"
            gapp.filedialog.asksaveasfilename = lambda **kw: str(destino_h)
            ventana.exportar_pdf_resumida()
            raiz.update()
            h["termino_a_tiempo"] = _esperar_pdf(ventana, raiz)
            h["estado_final"] = ventana.proceso_pdf.estado.value
            h["rotulo_final"] = ventana.lbl_estado_pdf.cget("text")
            h["existe"] = destino_h.is_file() and destino_h.stat().st_size > 0
        r["hidrologia"] = h

        # 5. Un gesto que invalida.
        ventana.cuencas_var.set(str(salida / "cuencas_cualquiera.csv"))
        raiz.update()
        r["tras_invalidar"] = {"informe_es_None": ventana.informe is None,
                               "exportadores": _exportadores(ventana),
                               "panel": _panel(ventana)}
        ventana.cuencas_var.set("")

        # 6. La corrida de perfil de la guia: la Fase 9 diferida.
        perfil = corrida("perfil_guia")
        _poner_corrida(ventana, perfil)
        informe = _correr(ventana, raiz)
        r["perfil"] = {
            "informe": informe is not None,
            "alcance": None if informe is None else informe.alcance,
            "panel": _panel(ventana),
            "lineas_de_la_cli": [] if informe is None else cli._lineas_cabezal(informe.cabezal),
            "error_visible": ventana.lbl_error_datos.cget("text")}

        # 7. Una corrida que falla.
        ventana.csv_var.set(str(salida / "no_existe.csv"))
        _correr(ventana, raiz)
        r["tras_fallo"] = {"informe_es_None": ventana.informe is None,
                           "exportadores": _exportadores(ventana),
                           "panel": _panel(ventana)}
        r["dialogos"] = dialogos
    finally:
        raiz.destroy()
    (salida / "resumen_ui2.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
