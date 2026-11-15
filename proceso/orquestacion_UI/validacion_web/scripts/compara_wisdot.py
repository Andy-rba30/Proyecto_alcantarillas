import json, sys, math
sys.path.insert(0, '/tmp/validacion_web/scripts')
from memoria_txt import por_punto
from conv import a_ft, FT
from hds5_mano import hw_entrada_ft, yn_ft, yc_ft, geo, G_FT
O = {o['id']: o for o in json.load(open('/tmp/ejemplos_web/obras_reales/obras.json'))['obras']}['OR-US-WI-03']
W = '/tmp/validacion_web/casos/OBRA_WISDOT'
def app(var):
    r = {}
    for D in ('2.0', '2.25', '2.5', '3.0'):
        r.update(por_punto(f'{W}/{var}/D{D}ft/salida/memoria.html'))
    return r
A, B = app('base'), app('alt')
filas, mano = [], {}
for c in O['cruces']:
    e = c['entradas']; n = c['cruce'].split()[-1]; D = e['D_ft']; L = e['L_ft']
    S = (e['invert_entrada_ft'] - e['invert_salida_ft']) / L
    for tag, clave in (('d', 'en_Q_diseno'), ('m', 'en_Q_max')):
        h = c['resultados_HY8'][clave]; q = h['Q_cfs']; pid = f'WI-C{n}-Q{tag}'
        a, b = A.get(pid, {}), B.get(pid, {})
        g = lambda k: (a[k][0] if k in a and isinstance(a[k][0], float) else None)
        # recalculo a mano (independiente de la app)
        hwi, reg = hw_entrada_ft(q, D, S)
        yc = yc_ft(q, D)
        try: yn12 = yn_ft(q, D, 0.012, S)
        except ValueError: yn12 = None
        try: yn13 = yn_ft(q, D, 0.013, S)
        except ValueError: yn13 = None
        Af = math.pi * D**2 / 4; V = q / Af; R = D / 4
        ho = max(h['TW_ft'] + (e['canal_TW']['invert_ft'] - e['invert_salida_ft']), (yc + D) / 2)
        Hs = {nn: (1 + 0.5 + 29.0 * nn**2 * L / R**(4/3)) * V**2 / (2 * G_FT) for nn in (0.012, 0.013)}
        hwo = {nn: Hs[nn] + ho - S * L for nn in Hs}
        mano[pid] = dict(HW_entrada_HDS5_ft=hwi, regimen=reg, yc_ft=yc, yn_n0012_ft=yn12, yn_n0013_ft=yn13,
                         HWo_aprox_n0012_ft=hwo[0.012], HWo_aprox_n0013_ft=hwo[0.013])
        fila = dict(id=pid, Q_cfs=q, D_ft=D, S=S, HY8=dict(HWi=h['prof_HW_control_entrada_ft'], HWo=h['prof_HW_control_salida_ft'],
                    control='salida' if h['prof_HW_control_salida_ft'] > h['prof_HW_control_entrada_ft'] else 'entrada', tipo=h['tipo_flujo'],
                    yn=h['yn_ft'], yc=h['yc_ft'], TW=h['TW_ft'], V=h['V_salida_fts'], HW_gob=max(h['prof_HW_control_entrada_ft'], h['prof_HW_control_salida_ft'])),
                    app=dict(HWi=g('HW_entrada') and a_ft(g('HW_entrada')), HWo_aprox=g('HW_salida') and a_ft(g('HW_salida')),
                             HWo_remanso=g('HW_remanso') and a_ft(g('HW_remanso')), HW_gob=g('HW') and a_ft(g('HW')), control=a.get('control'),
                             yn=g('y_normal') and a_ft(g('y_normal')), yc=g('y_c') and a_ft(g('y_c')), TW=g('TW') and a_ft(g('TW')),
                             V_salida=g('V_salida') and g('V_salida') / FT),
                    mano=mano[pid],
                    invariante_base_alt=all(a.get(k) == b.get(k) for k in set(a) | set(b)))
        filas.append(fila)
json.dump(filas, open('/tmp/validacion_web/casos/OBRA_WISDOT/contraste.json', 'w'), indent=1)
def p(x): return '—' if x is None else f'{x:.3f}'
def d(x, y): return '' if (x is None or y is None) else f' ({100*(x-y)/y:+.1f}%)'
for f in filas:
    H, Ap, M = f['HY8'], f['app'], f['mano']
    print(f"{f['id']:9s} Q={f['Q_cfs']:4.0f} D={f['D_ft']} S={f['S']:.4f} HY8 {H['tipo']:6s} ctrl {H['control']:7s}| app ctrl {Ap['control']} "
          f"| HWi {H['HWi']:.3f}/{p(Ap['HWi'])}{d(Ap['HWi'],H['HWi'])} mano {M['HW_entrada_HDS5_ft']:.3f} "
          f"| HWo {H['HWo']:.3f}/aprox {p(Ap['HWo_aprox'])} rem {p(Ap['HWo_remanso'])} mano12 {M['HWo_aprox_n0012_ft']:.3f} "
          f"| HWgob {H['HW_gob']:.3f}/{p(Ap['HW_gob'])}{d(Ap['HW_gob'],H['HW_gob'])} | yc {H['yc']:.3f}/{p(Ap['yc'])}{d(Ap['yc'],H['yc'])} "
          f"| yn {H['yn']:.3f}/{p(Ap['yn'])} m12 {p(M['yn_n0012_ft'])} | TW {H['TW']:.3f}/{p(Ap['TW'])} | V {H['V']:.3f}/{p(Ap['V_salida'])} | inv {f['invariante_base_alt']}")
