"""
tests/apoyo/gui_ext8_real.py
============================
EXT-8 SOBRE LA VENTANA DE VERDAD: el PDF fuera del hilo de Tk (PC-11) y la
accesibilidad minima (PC-17), medidos donde el AST no llega.

    python -m tests.apoyo.gui_ext8_real <directorio de salida>

Corre en un proceso limpio por la misma razon que `gui_corrida_perfil.py`:
`test_gui_contrato.py` instala dobles de `tkinter` y con ellos la ventana
seria un espejismo. Que se mide, en orden:

  1. el rotulo visible del motivo: con la ventana recien abierta dice por
     que los exportadores estan apagados, y tras una corrida queda vacio;
  2. la rueda: un `<Button-4>` sobre el canvas de la pestana 1 no revienta
     (X11 la manda asi) y `unidades_de_rueda` decide el sentido;
  3. Escape cierra la ventana normativa y la ayuda de entrada;
  4. Control-Return esta atado en la raiz y ejecuta el pipeline;
  5. exportar el PDF: si weasyprint esta operativo en ESTE interprete, sale
     por el subproceso --- el boton se apaga con `MOTIVO_EXPORTANDO_PDF`, el
     rotulo de estado cambia, el bucle `after` lo termina y el PDF existe ---;
     si no, sale por el navegador en este proceso y se registra que via fue.
     Se mide tambien que cancelar deja un estado terminal claro.
"""

import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

import cli                                             # noqa: E402

CSV_PERFIL = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"
EXTERNOS = {
    "globales": {"luz_m": 3.0, "L_hidraulico_m": 120.0},
    "puntos": {"C-01": {"Q_m3s": 0.65, "S_conducto": 0.004}},
}
CLAVE = "phi_relleno_trasdos"
LIMITE_ESPERA_S = 300.0


def _esperar_pdf(ventana, raiz):
    inicio = time.monotonic()
    while ventana.proceso_pdf is not None and not ventana.proceso_pdf.estado.terminal:
        raiz.update()
        time.sleep(0.05)
        if time.monotonic() - inicio > LIMITE_ESPERA_S:
            return False
    # Un giro mas para que `_sondear_pdf` pinte el estado terminal.
    for _ in range(10):
        raiz.update()
        time.sleep(0.05)
    return True


def main(salida: Path) -> int:
    import ttkbootstrap as tb
    import webbrowser

    import gui.app as gapp
    import gui.componentes as comp
    from gui import ayuda_entrada, ventana_normativa
    from src.modulos import M11_reporte as M11

    salida.mkdir(parents=True, exist_ok=True)
    externos = salida / "datos_externos.json"
    externos.write_text(json.dumps(EXTERNOS, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    dialogos = []
    gapp.messagebox.showinfo = lambda titulo, texto, *a, **k: dialogos.append(
        ("info", titulo, texto))
    gapp.messagebox.showerror = lambda titulo, texto, *a, **k: dialogos.append(
        ("error", titulo, texto))
    gapp.messagebox.askyesno = lambda *a, **k: True
    webbrowser.open = lambda *a, **k: True

    raiz = tb.Window(themename="litera")
    obs = {}
    try:
        ventana = gapp.ExpedienteApp(raiz)
        ventana.csv_var.set(str(CSV_PERFIL))
        ventana.datos_externos_var.set(str(externos))
        ventana.proyecto_var.set("EXT-8 ventana real")
        ventana.alcance_var.set(cli.ALCANCE_PERFIL)
        raiz.update()

        # 1. El rotulo visible del motivo.
        obs["rotulo_antes"] = ventana.btn_json.rotulo.cget("text")
        obs["motivo_sin_corrida"] = gapp.MOTIVO_SIN_CORRIDA

        # 2. La rueda en X11.
        canvas = ventana.tab_datos.canvas
        canvas.event_generate("<Enter>")
        canvas.event_generate("<Button-4>")
        canvas.event_generate("<Button-5>")
        raiz.update()
        obs["rueda_x11"] = (comp.unidades_de_rueda(num=4, delta=0),
                            comp.unidades_de_rueda(num=5, delta=0))
        obs["eventos_rueda"] = list(comp.MarcoScroll.EVENTOS_RUEDA)

        # 3. Escape cierra las emergentes.
        vn = ventana_normativa.VentanaNormativa(raiz, CLAVE)
        raiz.update()
        vn.event_generate("<Escape>")
        raiz.update()
        obs["normativa_cerrada_con_escape"] = not vn.winfo_exists()
        va = ayuda_entrada.VentanaAyudaEntrada(raiz)
        raiz.update()
        va.event_generate("<Escape>")
        raiz.update()
        obs["ayuda_cerrada_con_escape"] = not va.winfo_exists()

        # 4. Control-Return ejecuta.
        obs["control_return_atado"] = bool(raiz.bind("<Control-Return>"))
        raiz.event_generate("<Control-Return>")
        raiz.update()
        obs["informe_tras_control_return"] = ventana.informe is not None
        obs["rotulo_tras_correr"] = ventana.btn_json.rotulo.cget("text")
        obs["ayuda_pdf_nombra_umbral"] = str(
            gapp.expdf.UMBRAL_PUNTOS_PDF) in ventana.btn_pdf.ayuda

        # 5. El PDF.
        obs["weasyprint_disponible"] = M11.weasyprint_disponible()
        destino = salida / "memoria.pdf"
        gapp.filedialog.asksaveasfilename = lambda **kw: str(destino)
        ventana.exportar_pdf()
        raiz.update()
        if obs["weasyprint_disponible"]:
            obs["boton_pdf_apagado_durante"] = (
                str(ventana.btn_pdf.cget("state")) == "disabled")
            obs["motivo_durante"] = ventana.btn_pdf.motivo
            obs["cancelar_encendido_durante"] = (
                str(ventana.btn_cancelar_pdf.cget("state")) == "normal")
            obs["estado_pdf_durante"] = ventana.lbl_estado_pdf.cget("text")
            obs["termino_a_tiempo"] = _esperar_pdf(ventana, raiz)
            obs["estado_final"] = ventana.proceso_pdf.estado.value
            obs["pdf_existe"] = destino.is_file() and destino.stat().st_size > 0
            obs["boton_pdf_encendido_despues"] = (
                str(ventana.btn_pdf.cget("state")) == "normal")
            obs["rotulo_estado_final"] = ventana.lbl_estado_pdf.cget("text")
            # Y cancelar: otra exportacion, terminada a mano.
            destino2 = salida / "cancelada.pdf"
            gapp.filedialog.asksaveasfilename = lambda **kw: str(destino2)
            ventana.exportar_pdf()
            raiz.update()
            ventana._cancelar_pdf()
            obs["cancelacion_termino"] = _esperar_pdf(ventana, raiz)
            obs["estado_cancelado"] = ventana.proceso_pdf.estado.value
            obs["pdf_cancelado_no_existe"] = not destino2.exists()
            obs["rotulo_cancelado"] = ventana.lbl_estado_pdf.cget("text")
        else:
            obs["html_navegador_existe"] = destino.with_suffix(".html").is_file()
            obs["rotulo_estado_final"] = ventana.lbl_estado_pdf.cget("text")
        obs["dialogos"] = dialogos
    finally:
        raiz.destroy()
    (salida / "observado.json").write_text(
        json.dumps(obs, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
