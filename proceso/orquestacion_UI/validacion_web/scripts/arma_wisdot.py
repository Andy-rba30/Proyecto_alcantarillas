"""Obra real WisDOT STH 32 (proyecto 9190-26(27)-00), reporte HY-8: 9 cruces, tubo circular
de concreto, 'Square Edge with Headwall', n = 0.012 (la app NO puede tomarlo: el n del
concreto es [N] de la Tabla N 09, 0.010-0.013, y no es declarable).
PUBLICADO: Q de diseno y maximo, D, inverts, L, canal de salida (rectangular b = 8 ft,
S = 0.33, n = 0.029, invert), cota de cresta de la calzada.
DATOS DE PRUEBA: area_ha, cota_terreno, subrasante (rasante - paquete), CBR, esviaje, SUCS,
luz, altura_total del canal, espesor de pared (ASTM C76 pared B) y los ensayos de durabilidad
que dejan solo el concreto como candidato. Un solo escalon de diametro por corrida (el del
cruce): el siguiente supera el tope de 2.70 m, de modo que la hidraulica del cruce se lee
aunque el escalon no pase las verificaciones de la app (memoria)."""
import json, sys, csv
sys.path.insert(0, '/tmp/validacion_web/scripts')
from conv import ft, cfs
out, Dft, variante = sys.argv[1], float(sys.argv[2]), (sys.argv[3] if len(sys.argv) > 3 else 'base')
alt = variante == 'alt'
O = {o['id']: o for o in json.load(open('/tmp/ejemplos_web/obras_reales/obras.json'))['obras']}['OR-US-WI-03']
cols = "id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,cota_coronacion_canal".split(',')
filas, ext = [], {"globales": {"luz_m": 4.0 if alt else 3.0, "acceso_mantenimiento_previsto": True,
                  "resistividad_ohm_cm": 500, "abrasion": "severamente_abrasivo",
                  "seccion_receptor_medida": {"b_m": ft(8.0), "z_HV": 0.0, "S": 0.33, "n": 0.029, "altura_total_m": 2.0 if alt else 1.0}},
                  "puntos": {}}
k = 0
for c in O['cruces']:
    e = c['entradas']
    if abs(e['D_ft'] - Dft) > 1e-9: continue
    n = c['cruce'].split()[-1]
    S = (e['invert_entrada_ft'] - e['invert_salida_ft']) / e['L_ft']
    for tag, q in (('d', e['Q_diseno_cfs']), ('m', e['Q_max_cfs'])):
        k += 1
        pid = f'WI-C{n}-Q{tag}'
        ras = ft(e['cota_cresta_calzada_ft'])
        filas.append(dict(id=pid, progresiva_km=f'{int(n)}+{k*10:03d}', familia='A', Q_m3s=f'{cfs(q):.6f}', area_ha=300 if alt else 200,
            S_cauce=f'{S:.6f}', cota_terreno=f"{ft(e['invert_entrada_ft']) + (0.2 if alt else 0.0):.6f}", cota_rasante=f'{ras:.6f}',
            cota_subrasante=f"{ras - (0.30 if alt else 0.15):.6f}", cbr_subrasante=5 if alt else 10, esviaje_grados=0,
            ancho_plataforma=12.0 if alt else 10.0, cota_fondo_receptor=f"{ft(e['canal_TW']['invert_ft']):.6f}", Q_receptor_m3s=f'{cfs(q):.6f}',
            cota_TW='', sucs_fundacion='GW' if alt else 'SM', NF_profundidad_m='', cota_fondo_entrada=f"{ft(e['invert_entrada_ft']):.6f}", cota_coronacion_canal=''))
        ext['puntos'][pid] = {"longitud_m": ft(e['L_ft']), "S_conducto": round(S, 8)}
with open(f'{out}/puntos.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(filas)
json.dump(ext, open(f'{out}/externos.json', 'w'), indent=1)
Dm = ft(Dft); Dmm = round(Dm * 1000)
wall = {610: 0.0762, 686: 0.0826, 762: 0.0889, 914: 0.1016}
with open(f'{out}/declaraciones.txt', 'w') as f:
    f.write(f'# un solo escalon: D = {Dft} ft = {Dm} m; el siguiente supera el tope\n')
    f.write('diametros_normalizados={"inicio": %r, "paso": 5.0}\n' % Dm)
    f.write('espesor_pared_conducto={"concreto_reforzado": {%d: %r, 900: 0.1}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}\n' % (Dmm, wall[Dmm] * (1.25 if alt else 1.0)))
print(len(filas), 'puntos')
