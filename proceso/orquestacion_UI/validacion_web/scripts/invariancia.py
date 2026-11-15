"""Demuestra que los DATOS DE PRUEBA no mueven las magnitudes comparadas: compara las
variantes base y alt (que cambian solo datos de prueba) de cada caso."""
import json
W = '/tmp/validacion_web/casos'
out = {}
def dis(r): return {p['id']: p for p in json.load(open(r))['puntos']}
def maxdif(a, b, claves):
    m = 0.0
    for pid in a:
        da, db = a[pid]['diseno'], b[pid]['diseno']
        if da is None or db is None:
            if (da is None) != (db is None): return float('inf')
            continue
        for k in claves: m = max(m, abs(da[k] - db[k]))
    return m
K = ['HW_entrada_m', 'y_normal_m', 'y_critico_m', 'TW_m', 'V_sedimentacion_m_s', 'V_salida_m_s', 'h_o_m']
for caso in ('TDOT_EX2', 'TDOT_EX1', 'UNC_ALC36', 'UPAO_MANNING'):
    a, b = dis(f'{W}/{caso}/base/salida/cli.informe.json'), dis(f'{W}/{caso}/alt/salida/cli.informe.json')
    out[caso] = {'max_dif_abs_hidraulica_m_o_m_s': maxdif(a, b, K),
                 'mismo_diseno': all((a[i]['diseno'] or {}).get('seccion') == (b[i]['diseno'] or {}).get('seccion') for i in a)}
# EX4: escalon descartado (memoria y motivo)
a, b = dis(f'{W}/TDOT_EX4/base/salida/cli.informe.json'), dis(f'{W}/TDOT_EX4/alt/salida/cli.informe.json')
out['TDOT_EX4'] = {'motivo_V4b_igual': all(a[i]['iteraciones'][0]['motivo'] == b[i]['iteraciones'][0]['motivo'] for i in a),
                   'max_dif_TW_m': max(abs(a[i]['datos_declarados']['TW_m']['valor'] - b[i]['datos_declarados']['TW_m']['valor']) for i in a)}
for t in ('TR100_50', 'TR500_100'):
    a, b = dis(f'{W}/HIDRO_UPAO_UNC/base/salida/cli_{t}.informe.json'), dis(f'{W}/HIDRO_UPAO_UNC/alt/salida/cli_{t}.informe.json')
    r = {}
    for pid in a:
        ca, cb = a[pid]['caudal'] or {}, b[pid]['caudal'] or {}
        r[pid] = {k: (ca.get(k) == cb.get(k)) for k in ('P24_TR_mm', 'tc_min', 'K_uniformidad', 'I_mm_h', 'C', 'TR_anios')}
    out[f'HIDRO_{t}'] = r
json.dump(out, open('/tmp/validacion_web/invariancia.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
