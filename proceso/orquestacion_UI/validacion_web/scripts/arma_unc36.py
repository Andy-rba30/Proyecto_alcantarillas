"""UNC Cocahuayco, hoja 'Capacidad hidraulica de una alcantarilla de quebrada D=36"' (pp. 90-91):
PUBLICADO: D = 0.90 m TMC, S0 = 3.5 %, L = 5.00 m, Y4 (tirante aguas abajo) = 0.50 m,
Q = 0.80 m3/s (Q definitivo; Qc = 0.79), Y1 = 0.80 m, yc = 0.51 m (metodo de French).
DATOS DE PRUEBA: cotas, CBR, esviaje, sucs, luz, area. Para que la app evalue el TMC
(el concreto va primero en su orden y pasaria) se declara v_max_concreto_eleccion = 3.0 m/s
(minimo de su ventana): el concreto queda fuera por V3 en todos sus diametros. Ese
criterio no entra en la hidraulica del TMC."""
import csv, json, sys
out, v = sys.argv[1], sys.argv[2]
alt = v == 'alt'
cols = "id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,cota_coronacion_canal".split(',')
rows = []
for pid, q in (('UNC36-Q0p80', 0.80), ('UNC36-Q0p79', 0.79)):
    rows.append(dict(id=pid, progresiva_km='0+100' if q == 0.80 else '0+200', familia='A', Q_m3s=q, area_ha=80 if alt else 50, S_cauce=0.035,
        cota_terreno=100.0, cota_rasante=103.5 if alt else 102.5, cota_subrasante=103.35 if alt else 102.35, cbr_subrasante=6 if alt else 10,
        esviaje_grados=0, ancho_plataforma=7.0, cota_fondo_receptor=99.70 if alt else 99.80, Q_receptor_m3s='', cota_TW='',
        sucs_fundacion='GW' if alt else 'SM', NF_profundidad_m='', cota_fondo_entrada=100.0, cota_coronacion_canal=''))
with open(f'{out}/puntos.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
json.dump({"globales": {"luz_m": 4.0 if alt else 3.0, "longitud_m": 5.0, "S_conducto": 0.035, "TW_m": 0.50, "acceso_mantenimiento_previsto": True}},
          open(f'{out}/externos.json', 'w'), indent=1)
