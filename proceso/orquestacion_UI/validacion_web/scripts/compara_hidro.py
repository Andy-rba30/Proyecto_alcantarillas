import json, sys
def lee(r):
    d = json.load(open(r)); o = {}
    for p in d['puntos']:
        c = p['caudal'] or {}
        o[p['id']] = dict(Q=c.get('Q_m3s'), TR=c.get('TR_anios') or (p['clasificacion'] or {}).get('TR_anios'), tc_min=c.get('tc_min'),
            dur=c.get('duracion_min'), I=c.get('I_mm_h'), C=c.get('C'), K=c.get('K_uniformidad'), P24=c.get('P24_TR_mm'),
            dist=c.get('distribucion'), bloqueos=[(b['tipo'], b['etapa'], (b.get('mensaje') or '')[:400]) for b in p['bloqueos'] if 'Hidrologia' in b['fase'] or 'hidrolog' in b['etapa'].lower() or 'caudal' in b['etapa']])
    return o
for r in sys.argv[1:]:
    print('==', r)
    for k, v in lee(r).items():
        print(f"  {k:13s} TR={v['TR']} P24={v['P24']} tc_min={v['tc_min']} dur={v['dur']} I={v['I']} C={v['C']} K={v['K']} Q={v['Q']}")
        for b in v['bloqueos']: print('      BLOQUEO', b)
