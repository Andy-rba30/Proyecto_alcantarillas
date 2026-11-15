import json, sys
sys.path.insert(0, '/tmp/validacion_web/scripts')
from conv import a_ft, a_cfs, FT
ej = {e['id']: e for e in json.load(open('/tmp/ejemplos_web/ejemplos.json'))}['TDOT-EX2-circ-HY8']
tabla = ej['resultados_publicados']['tabla_por_caudal']
def lee(ruta):
    d = json.load(open(ruta)); out = {}
    for p in d['puntos']:
        di = p['diseno']
        out[p['id']] = dict(dimensionado=p['dimensionado'], seccion=di and di['seccion'],
            control=di and di['control_gobernante'], HW_e=di and di['HW_entrada_m'], HW_s=di and di['HW_salida_m'],
            HW=di and di['HW_gobernante_m'], yn=di and di['y_normal_m'], yc=di and di['y_critico_m'],
            TW=di and di['TW_m'], Vsed=di and di['V_sedimentacion_m_s'], Vsal=di and di['V_salida_m_s'],
            ysal=di and di['y_salida_m'], ho=di and di['h_o_m'],
            salida_no_se_forma=None)
    return out
base = lee(sys.argv[1]); alt = lee(sys.argv[2]) if len(sys.argv) > 2 else None
filas = []
for f in tabla:
    pid = f"Q{f['Q_cfs']:04.1f}cfs".replace('.', 'p'); a = base[pid]
    pub = dict(HW=f['HW_elev_ft'] - 341.25, yn=f['normal_ft'], yc=f['critico_ft'], TW=f['TW_ft'], V=f['V_salida_fps'], ysal=f['profundidad_salida_ft'])
    app = dict(HW=a_ft(a['HW_e']), yn=a_ft(a['yn']), yc=a_ft(a['yc']), TW=a_ft(a['TW']), V=a['Vsed']/FT, ysal=a_ft(a['ysal']), Vsal_nmin=a['Vsal']/FT, HWs=a_ft(a['HW_s']) if a['HW_s'] is not None else None)
    inv = None
    if alt:
        b = alt[pid]
        inv = max(abs(a[k]-b[k]) for k in ('HW_e','yn','yc','TW','Vsed','Vsal'))
    filas.append(dict(id=pid, Q_cfs=f['Q_cfs'], control_app=a['control'], seccion=a['seccion'], publicado=pub, app=app,
        dif_pct={k: 100*(app[k]-pub[k])/pub[k] for k in pub}, max_dif_abs_entre_variantes_m=inv))
for r in filas:
    print(f"{r['id']:9s} Q={r['Q_cfs']:5.1f} {r['control_app']:8s} " + ' '.join(f"{k}: pub {r['publicado'][k]:.3f} app {r['app'][k]:.3f} ({r['dif_pct'][k]:+.1f}%)" for k in ('HW','yn','yc','TW','V','ysal')) + f" | Vsal(nmin) {r['app']['Vsal_nmin']:.3f} | HWsal {r['app']['HWs']} | inv {r['max_dif_abs_entre_variantes_m']}")
json.dump(filas, open(sys.argv[3] if len(sys.argv) > 3 else '/dev/null', 'w'), indent=1)
