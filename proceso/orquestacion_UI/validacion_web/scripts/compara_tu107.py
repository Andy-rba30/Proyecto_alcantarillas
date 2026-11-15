import json, math, statistics as st
from scipy.stats import norm
W = '/tmp/validacion_web/casos/OBRA_TU107'
O = {o['id']: o for o in json.load(open('/tmp/ejemplos_web/obras_reales/obras.json'))['obras']}['OR-PE-TU107-04']
cu = {c['cuenca']: c for c in O['entradas']['tabla_26_27_cuencas']}
t66 = {r['cuenca']: r for r in O['resultados']['Tabla_66_Q_racional_36_cuencas']}
def lee(r): return {p['id']: (p['caudal'] or {}, p) for p in json.load(open(r))['puntos']}
dp, t4 = lee(f'{W}/base/salida/cli_dick_peschke.informe.json'), lee(f'{W}/base/salida/cli_tabla04.informe.json')
dpa, t4a = lee(f'{W}/alt/salida/cli_dick_peschke.informe.json'), lee(f'{W}/alt/salida/cli_tabla04.informe.json')
serie = [float(v) for v in O['entradas']['serie_P24_max_mm'].values()]
ln = [math.log(x) for x in serie]; mu, s = st.mean(ln), st.stdev(ln)
mano = {'LN2P_ln_media': mu, 'LN2P_ln_desv': s, 'log10_media': mu / math.log(10), 'log10_desv': s / math.log(10)}
for T in (35, 70, 71):
    mano[f'P24_T{T}_serie'] = math.exp(mu + norm.ppf(1 - 1/T) * s)
    mano[f'P24_T{T}_publicados_log10'] = 10 ** (2.117 + norm.ppf(1 - 1/T) * 0.389)
temez = lambda L, S: 0.3 * (L / S**0.25)**0.76
filas = []
for cid, c in cu.items():
    a = dp[cid][0]; b = t4[cid][0]; p = dp[cid][1]
    tr = p['clasificacion']['TR_anios'] if p['clasificacion'] else None
    col = '35' if tr == 35 else '70'
    tez_pdf = c['tc_bransby_h']        # OJO: en el PDF (Tabla 27) la 2a columna es TEMEZ; ejemplos/obras.json las rotula al reves
    S_cotas = (c['cota_max'] - c['cota_min']) / (c['L_cauce_km'] * 1000)
    f = dict(cuenca=cid, A=c['area_km2'], TR_app=tr, TR_tesis=int(col),
             Tc_temez_pdf_h=tez_pdf, Tc_bw_pdf_h=c['tc_temez_h'], Tc_app_h=a.get('tc_min') and a['tc_min'] / 60,
             Tc_mano_S_publicada_h=temez(c['L_cauce_km'], c['S_mm']), Tc_mano_S_de_cotas_h=temez(c['L_cauce_km'], S_cotas),
             dur_tesis_min=c['duracion_min'], C_tesis=t66.get(cid, {}).get('C'), C_app=a.get('C'),
             I_tesis=t66.get(cid, {}).get('I_mmh', {}).get(col), I_app_DP=a.get('I_mm_h'), I_app_T04=b.get('I_mm_h'),
             I_mano_IDF_tesis=408.8108 * int(col)**0.3910 / c['duracion_min']**0.5375,
             Q_tesis=t66.get(cid, {}).get('Q_m3s', {}).get(col), Q_app_DP=a.get('Q_m3s'), Q_app_T04=b.get('Q_m3s'),
             bloqueo=[bb['mensaje'][:200] for bb in p['bloqueos'] if 'Hidrolog' in bb['fase']],
             invariante=all(dp[cid][0].get(k) == dpa[cid][0].get(k) for k in ('P24_TR_mm', 'tc_min', 'I_mm_h', 'C', 'Q_m3s')) and
                        all(t4[cid][0].get(k) == t4a[cid][0].get(k) for k in ('P24_TR_mm', 'tc_min', 'I_mm_h', 'C', 'Q_m3s')))
    filas.append(f)
json.dump({'mano': mano, 'filas': filas, 'P24_app': {'T35': dp['C-1'][0]['P24_TR_mm'], 'T71': dp['C-5'][0]['P24_TR_mm']},
           'KS_app': [(x['distribucion'], x['D'], x['d_critico'], x['acepta'], x['P_TR_mm']) for x in dp['C-1'][0]['ajustes']]},
          open(f'{W}/contraste.json', 'w'), indent=1)
print(json.dumps(mano, indent=1))
pr = lambda x, n=3: '—' if x is None else f'{x:.{n}f}'
for f in filas:
    dq = '' if not (f['Q_tesis'] and f['Q_app_T04']) else f"{100*(f['Q_app_T04']/f['Q_tesis']-1):+.1f}%"
    print(f"{f['cuenca']:5s} A={f['A']:6.2f} TR {f['TR_app']}/{f['TR_tesis']} Tc pdfTemez {f['Tc_temez_pdf_h']:.2f} app {pr(f['Tc_app_h'])} manoS {f['Tc_mano_S_publicada_h']:.3f} manoCot {f['Tc_mano_S_de_cotas_h']:.3f} | C {f['C_tesis']}/{f['C_app']} | I tesis {pr(f['I_tesis'],1)} idfmano {f['I_mano_IDF_tesis']:.1f} DP {pr(f['I_app_DP'],1)} T04 {pr(f['I_app_T04'],1)} | Q tesis {f['Q_tesis']} DP {pr(f['Q_app_DP'],2)} T04 {pr(f['Q_app_T04'],2)} {dq} | inv {f['invariante']} {'BLOQ' if f['bloqueo'] else ''}")
