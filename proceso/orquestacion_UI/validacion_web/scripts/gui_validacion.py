"""Conductor de la VENTANA REAL (gui.app, ttkbootstrap) bajo xvfb para la validacion
externa. Imita tests/apoyo/gui_ui4_recorrido_real.py: carga las entradas por los botones
«Examinar...» de la pestaña 1 (el dialogo devuelve la ruta), declara los criterios por
la pestaña 2 («Valor nuevo» + «Aplicar solo a esta corrida», con la nota si la puerta
la exige), pulsa EJECUTAR, lee la pestaña 3 (detalle de puntos) y exporta el JSON con
«Exportar JSON» (pestaña 4). Despues compara ese JSON con el de la CLI (sin la hora).
Uso (desde /home/user/val_web):
  xvfb-run -a python /tmp/validacion_web/scripts/gui_validacion.py <caso> <salida>
"""
import json, sys, time, traceback
from pathlib import Path
sys.path.insert(0, '/home/user/val_web')
import cli
from src import criterios_adoptados as ca
from src import sesion as ses
from src import comparador as compa

V = Path('/tmp/validacion_web/casos')
NOTA = 'DATOS DE PRUEBA: validacion externa (nota que la puerta exige)'
CASOS = {
  'tdot_ex2': dict(csv=V/'TDOT_EX2/base/puntos.csv', externos=V/'TDOT_EX2/base/externos.json',
                   sitio=V/'TDOT_EX2/base/sitio.json', cuencas=None, estacion=None, alcance='perfil',
                   decl=V/'TDOT_EX2/declaraciones_base.txt', cli_json=V/'TDOT_EX2/base/salida/cli.informe.json',
                   detalles=('Q25p0cfs', 'Q02p5cfs')),
  'wisdot': dict(csv=V/'OBRA_WISDOT/base/D2.5ft/puntos.csv', externos=V/'OBRA_WISDOT/base/D2.5ft/externos.json',
                 sitio=None, cuencas=None, estacion=None, alcance='perfil',
                 decl=V/'OBRA_WISDOT/base/D2.5ft/declaraciones.txt', cli_json=V/'OBRA_WISDOT/base/D2.5ft/salida/cli.informe.json',
                 detalles=('WI-C9-Qd', 'WI-C3-Qd')),
  'hidro': dict(csv=V/'HIDRO_UPAO_UNC/base/puntos.csv', externos=V/'HIDRO_UPAO_UNC/base/externos.json',
                sitio=V/'HIDRO_UPAO_UNC/base/sitio.json', cuencas=V/'HIDRO_UPAO_UNC/base/cuencas.csv',
                estacion=V/'HIDRO_UPAO_UNC/base/estacion.csv', alcance='perfil',
                decl=V/'HIDRO_UPAO_UNC/declaraciones_TR100_50.txt',
                cli_json=V/'HIDRO_UPAO_UNC/base/salida/cli_TR100_50.informe.json',
                detalles=('TINAS', 'TINAS-T-DIAG', 'UNC-A1')),
}

def leer_decl(ruta):
    import ast
    out = {}
    for l in open(ruta):
        l = l.strip()
        if not l or l.startswith('#'): continue
        k, v = l.split('=', 1)
        try: out[k] = ast.literal_eval(v)
        except Exception: out[k] = v
    return out

def pulsar_examinar(gapp, ventana, raiz, metodo, ruta):
    pend = [ventana.tab_datos]
    while pend:
        w = pend.pop(); pend.extend(w.winfo_children())
        if w.winfo_class() == 'TButton' and str(w.cget('command')).endswith(metodo):
            gapp.filedialog.askopenfilename = lambda **kw: str(ruta)
            w.invoke(); raiz.update(); return True
    return False

def declarar(ventana, raiz, clave, valor):
    ventana.nb.select(ventana.tab_criterios)
    ventana.filtro_texto_var.set(''); raiz.update()
    ventana.tree_criterios_todos.selection_set(clave); ventana.tree_criterios_todos.see(clave); raiz.update()
    ventana.valor_declarado_var.set(valor if isinstance(valor, str) else repr(valor)); raiz.update()
    ventana.btn_aplicar_corrida.boton.invoke(); raiz.update()
    primer = ventana.lbl_estado_criterio.cget('text'); con_nota = False
    if clave not in ca.valores_dinamicos() and ventana.editor is not None:
        ventana.editor.nota_var.set(NOTA); raiz.update()
        ventana.btn_aplicar_corrida.boton.invoke(); raiz.update(); con_nota = True
    return dict(declarado=clave in ca.valores_dinamicos(),
                mismo_valor=repr(ca.valores_dinamicos().get(clave)) == repr(valor),
                con_nota=con_nota, primer_rotulo=primer, rotulo=ventana.lbl_estado_criterio.cget('text'))

def main(caso, salida):
    import ttkbootstrap as tb, webbrowser
    import gui.app as gapp
    salida.mkdir(parents=True, exist_ok=True)
    c = CASOS[caso]; r = {'caso': caso, 'entradas': {k: str(v) for k, v in c.items() if k != 'detalles'}}
    dialogos = []
    gapp.messagebox.showinfo = lambda t, x, *a, **k: dialogos.append(['info', t, x])
    gapp.messagebox.showerror = lambda t, x, *a, **k: dialogos.append(['error', t, x])
    gapp.messagebox.askyesno = lambda *a, **k: True
    webbrowser.open = lambda *a, **k: True
    raiz = tb.Window(themename='litera')
    try:
        ventana = gapp.ExpedienteApp(raiz); raiz.update()
        ventana.proyecto_var.set({'tdot_ex2': 'Validacion TDOT Ej.2 (HY-8) base', 'wisdot': 'Obra real WisDOT STH 32 D=2.5 ft base',
                                  'hidro': 'Validacion hidrologia UPAO/UNC'}[caso])
        ventana.nb.select(ventana.tab_datos)
        ex = {'csv': pulsar_examinar(gapp, ventana, raiz, '_elegir_csv', c['csv']),
              'externos': pulsar_examinar(gapp, ventana, raiz, '_elegir_datos_externos', c['externos']),
              'sitio': pulsar_examinar(gapp, ventana, raiz, '_elegir_datos_sitio', c['sitio']) if c['sitio'] else 'sin sitio.json'}
        if c['cuencas']:
            ex['cuencas'] = pulsar_examinar(gapp, ventana, raiz, '_elegir_cuencas', c['cuencas'])
            ex['estacion'] = pulsar_examinar(gapp, ventana, raiz, '_elegir_estacion', c['estacion'])
        ventana.alcance_var.set(c['alcance']); raiz.update()
        r['examinar'] = ex
        r['campos_pestana_1'] = {n: getattr(ventana, n).get() for n in ('proyecto_var', 'csv_var', 'datos_externos_var', 'datos_sitio_var', 'cuencas_var', 'estacion_var', 'alcance_var')}
        r['declaraciones'] = {k: declarar(ventana, raiz, k, v) for k, v in leer_decl(c['decl']).items()}
        t0 = time.monotonic()
        ventana.btn_ejecutar.boton.invoke(); raiz.update()
        r['segundos_ejecucion'] = round(time.monotonic() - t0, 2)
        inf = ventana.informe
        r['informe'] = inf is not None
        r['error_visible'] = ventana.lbl_error_datos.cget('text')
        if inf is not None:
            # pestaña 3: filas y detalle
            ventana.nb.select(ventana.tab_puntos); raiz.update()
            r['pestana_3_filas'] = [list(ventana.tree_puntos.item(i, 'values')) for i in ventana.tree_puntos.get_children()]
            det = {}
            for pid in c['detalles']:
                ventana.tree_puntos.selection_set(pid); ventana.tree_puntos.see(pid); raiz.update()
                punto = next(p for p in inf.puntos if p.punto.id == pid)
                texto = ventana.txt_detalle.get('1.0', 'end-1c')
                lineas_cli = list(cli._lineas_punto(punto))
                import re
                norm = lambda x: re.sub(r'\s+', ' ', x).strip()
                lineas_v = [norm(x) for x in texto.splitlines()]
                faltan = [l for l in lineas_cli if l.strip().strip('-') and norm(l) not in lineas_v]
                det[pid] = {'texto': texto, 'lineas_de_la_cli_presentes_en_la_ventana (espacios normalizados, sin reglas ----)': len(faltan) == 0,
                            'n_lineas_cli': len(lineas_cli), 'lineas_cli_que_faltan': faltan[:10]}
            r['pestana_3_detalle'] = det
            # pestaña 4: exportar JSON por su boton
            ventana.nb.select(ventana.tab_resumen); raiz.update()
            destino = salida / 'ventana.informe.json'
            gapp.filedialog.asksaveasfilename = lambda **kw: str(destino)
            ventana.btn_json.boton.invoke(); raiz.update()
            r['json_exportado'] = destino.is_file()
            # sesion guardada (para reproducir con cli.py --sesion)
            barra = {}
            pend = [raiz]
            while pend:
                w = pend.pop(); pend.extend(w.winfo_children())
                if w.winfo_class() == 'TButton': barra.setdefault(str(w.cget('text')), w)
            ses_dest = salida / 'ventana.sesion.json'
            gapp.filedialog.asksaveasfilename = lambda **kw: str(ses_dest)
            barra['Guardar sesion'].invoke(); raiz.update()
            r['sesion_guardada'] = ses_dest.is_file()
            # equivalencia con la CLI
            vj = json.loads(destino.read_text(encoding='utf-8'))
            cj = json.loads(Path(c['cli_json']).read_text(encoding='utf-8'))
            a, b = ses.sin_marca_de_tiempo(vj), ses.sin_marca_de_tiempo(cj)
            r['json_igual_a_la_cli_sin_hora'] = a == b
            difs = []
            def dif(x, y, ruta=''):
                if type(x) != type(y): difs.append((ruta, repr(x)[:200], repr(y)[:200])); return
                if isinstance(x, dict):
                    for k in sorted(set(x) | set(y)):
                        if k not in x or k not in y: difs.append((ruta + '/' + k, repr(x.get(k))[:200], repr(y.get(k))[:200]))
                        else: dif(x[k], y[k], ruta + '/' + k)
                elif isinstance(x, list):
                    if len(x) != len(y): difs.append((ruta, f'len {len(x)}', f'len {len(y)}'))
                    for i, (p, q) in enumerate(zip(x, y)): dif(p, q, f'{ruta}[{i}]')
                elif x != y: difs.append((ruta, repr(x)[:200], repr(y)[:200]))
            dif(a, b)
            r['diferencias_ventana_vs_cli'] = difs[:60]
            r['n_diferencias'] = len(difs)
            cmp = compa.comparar(vj, cj)
            r['comparador'] = {'iguales': cmp.iguales, 'lineas': cmp.lineas()[:30]}
    except Exception:
        r['error'] = traceback.format_exc()
    finally:
        raiz.destroy()
    r['dialogos'] = dialogos
    (salida / 'recorrido_ventana.json').write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({k: r.get(k) for k in ('caso', 'informe', 'json_exportado', 'json_igual_a_la_cli_sin_hora', 'n_diferencias', 'segundos_ejecucion', 'error')}, ensure_ascii=False))
    return 0 if 'error' not in r else 1

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1], Path(sys.argv[2])))
