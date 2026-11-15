"""Obra real TU-107 Bocapan-Tamarindo (tesis UNTumbes 2026): hidrologia de 41 cuencas.
PUBLICADO: serie P24 de Canaveral TAL CUAL (Tablas 23-24, 40 anios, con sus valores de 729 mm
y filas repetidas), A, L, S de cada cuenca (Tabla 26; S con 2 decimales tal como se publica).
INFERIDO (no publicado como dato, rotulado): cobertura 'bosques_densa_vegetacion' + suelo
'permeable' + S_terreno = S del cauce: es la UNICA fila de la Tabla N 08 que reproduce las 36 C
publicadas (0.10 / 0.15 / 0.20 segun la clase de pendiente). Por eso el C de la app NO es un
contraste independiente: solo comprueba la lectura de la tabla.
DATOS DE PRUEBA: la columna fen (la tesis no la declara), todo lo hidraulico del CSV de puntos.
Metodo de Tc por cuenca: temez (la tesis promedia Temez y Bransby-Williams; la app no tiene
Bransby-Williams)."""
import csv, json, sys
out, var = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'base')
alt = var == 'alt'
O = {o['id']: o for o in json.load(open('/tmp/ejemplos_web/obras_reales/obras.json'))['obras']}['OR-PE-TU107-04']
serie = O['entradas']['serie_P24_max_mm']
fen = {'1983', '1997', '1998'} if alt else set()
with open(f'{out}/estacion.csv', 'w') as f:
    f.write('# Serie PUBLICADA tal cual: P24 max anual, estacion Canaveral (tesis UNTumbes 2026, Tablas 23-24).\n'
            '# La columna fen es DATO DE PRUEBA (la tesis no declara anios FEN).\n')
    f.write('estacion,anio,p24_mm,fen\n')
    for a, p in serie.items(): f.write(f'CANAVERAL,{a},{p},{"si" if a in fen else "no"}\n')
cu = O['entradas']['tabla_26_27_cuencas']
with open(f'{out}/cuencas.csv', 'w') as f:
    f.write('# 41 cuencas de la Tabla 26 (A, L, S publicados). cobertura/suelo/S_terreno INFERIDOS de la C\n'
            '# publicada (bosques_densa_vegetacion, permeable, S del cauce); ver arma_tu107.py.\n')
    f.write('id,area_km2,L_cauce_m,S_cauce_cuenca,S_terreno,cobertura,suelo,estacion,metodo_tc,H_desnivel_m,ajuste_kirpich,CN\n')
    for c in cu:
        f.write(f"{c['cuenca']},{c['area_km2']},{c['L_cauce_km']*1000:.0f},{c['S_mm']},{c['S_mm']},bosques_densa_vegetacion,permeable,CANAVERAL,temez,{c['cota_max']-c['cota_min']},,\n")
cols = "id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,cota_coronacion_canal".split(',')
with open(f'{out}/puntos.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for c in cu:
        w.writerow(dict(id=c['cuenca'], progresiva_km=c['progresiva'], familia='A', Q_m3s='', area_ha=f"{c['area_km2']*100:.6g}", S_cauce=0.02,
            cota_terreno=100.0, cota_rasante=104.5 if alt else 104.0, cota_subrasante=104.35 if alt else 103.85, cbr_subrasante=12 if alt else 10,
            esviaje_grados=0, ancho_plataforma=8.0, cota_fondo_receptor=99.0, Q_receptor_m3s='', cota_TW='', sucs_fundacion='SM',
            NF_profundidad_m='', cota_fondo_entrada='', cota_coronacion_canal=''))
json.dump({"globales": {"luz_m": 4.0 if alt else 3.0, "TW_m": 0.4 if alt else 0.3, "acceso_mantenimiento_previsto": True}},
          open(f'{out}/externos.json', 'w'), indent=1)
