"""UPAO La Jalca, tabla de diseno hidraulico de alcantarillas TMC (pp. 121-123): Manning a
seccion parcial con n = 0.024 y y/D ~ 0.75. Se toman 5 filas (N 1, 13, 40, 44 de paso; 46 de
alivio). PUBLICADO: Q total y S (unidad no publicada; la tabla es consistente con m/m).
DATOS DE PRUEBA: cotas, CBR, esviaje, sucs, luz, area, TW y los datos de la cuneta del alivio.
Se compara solo el DIAMETRO COMERCIAL (tesis: 24 in salvo N 40 y N 44, 36 in)."""
import csv, json, sys
out, v = sys.argv[1], sys.argv[2]
alt = v == 'alt'
filas = [(1, 0.236, 0.31, 'A'), (13, 1.076, 0.25, 'A'), (40, 4.042, 0.21, 'A'), (44, 2.422, 0.38, 'A'), (46, 0.317, 0.39, 'B')]
cols = "id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,cota_coronacion_canal".split(',')
rows = []
for k, (n, q, s, fam) in enumerate(filas):
    rows.append(dict(id=f'ALC{n:02d}', progresiva_km=f'{41+k}+{"500" if alt else "000"}', familia=fam, Q_m3s=q, area_ha=(30 if alt else 20) if fam == 'A' else 2,
        S_cauce=s, cota_terreno=100.0, cota_rasante=104.0 if alt else 103.0, cota_subrasante=103.85 if alt else 102.85, cbr_subrasante=6 if alt else 10,
        esviaje_grados=0, ancho_plataforma=7.0, cota_fondo_receptor=98.5 if alt else 98.8, Q_receptor_m3s='', cota_TW='', sucs_fundacion='GW' if alt else 'SM',
        NF_profundidad_m='', cota_fondo_entrada='', cota_coronacion_canal=''))
with open(f'{out}/puntos.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
json.dump({"globales": {"luz_m": 4.0 if alt else 3.0, "TW_m": 0.4 if alt else 0.3, "acceso_mantenimiento_previsto": True},
           "puntos": {"ALC46": {"L_hidraulico_m": 150.0 if alt else 120.0, "S_cuneta": 0.012 if alt else 0.01, "inicio_tramo_cuneta_km": 45.4 if alt else 44.9}}},
          open(f'{out}/externos.json', 'w'), indent=1)
