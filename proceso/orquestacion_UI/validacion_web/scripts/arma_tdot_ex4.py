"""TDOT Ejemplo 4 (HY-8), solo la parte de entrada cuadrada con cabezal (Type U):
Q = 90 cfs de diseno; el rebose de la calzada (cota 347.00 ft) empieza hacia
69.2 cfs, es decir, a 69.2 cfs el HW del 36 in llega a 347.00 ft (HW = 5.75 ft
sobre el invert 341.25). Invert de salida 337.95 ft; L = 110.05 ft (HY-8);
S = 0.03; cauce de salida trapezoidal b = 4 ft, z = 3:1, n = 0.065, S = 0.03,
fondo 337.95 ft (Fig. 6A-30c). n del barril: el ejemplo no lo repite para
la entrada cuadrada; la app usa el n de la Tabla 09 (0.010-0.013), no se declara.
DATOS DE PRUEBA: area_ha, terreno, rasante/subrasante (subida: la calzada real
de 347.00 ft no alcanza el resguardo MTC con HW/D ~ 1.9), cbr, esviaje, sucs,
luz, altura_total del cauce, y los ensayos de durabilidad que dejan solo el
concreto como candidato (resistividad < 1000 excluye TMC; abrasion severa
excluye HDPE) -- no tocan la hidraulica."""
import json, sys, csv
sys.path.insert(0, '/tmp/validacion_web/scripts')
from conv import ft, cfs
out, variante = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'base')
P = dict(base=dict(area_ha=50.0, terr=0.0, paq=0.15, cbr=10.0, sucs='SM', luz=3.0, extra=3.0, h=3.0),
         alt=dict(area_ha=500.0, terr=0.30, paq=0.30, cbr=4.0, sucs='GW', luz=5.0, extra=4.0, h=6.0))[variante]
inv_ent = ft(341.25); L = ft(110.05); inv_sal = inv_ent - 0.03 * L; ras = ft(347.00) + P['extra']
cols = "id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,cota_coronacion_canal".split(',')
filas = []
for i, q in enumerate([69.2, 72.0, 90.0]):
    filas.append(dict(id=f"EX4-Q{q:g}".replace('.', 'p'), progresiva_km=f"0+{100*(i+1):03d}", familia='A', Q_m3s=f"{cfs(q):.6f}", area_ha=P['area_ha'], S_cauce='0.03',
        cota_terreno=f"{inv_ent+P['terr']:.6f}", cota_rasante=f"{ras:.6f}", cota_subrasante=f"{ras-P['paq']:.6f}",
        cbr_subrasante=P['cbr'], esviaje_grados=0, ancho_plataforma=f"{ft(50):.6f}", cota_fondo_receptor=f"{inv_sal:.6f}",
        Q_receptor_m3s=f"{cfs(q):.6f}", cota_TW='', sucs_fundacion=P['sucs'], NF_profundidad_m='', cota_fondo_entrada=f"{inv_ent:.6f}", cota_coronacion_canal=''))
with open(f"{out}/puntos.csv", 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(filas)
json.dump({"globales": {"luz_m": P['luz'], "longitud_m": L, "S_conducto": 0.03,
           "seccion_receptor_medida": {"b_m": ft(4.0), "z_HV": 3.0, "S": 0.03, "n": 0.065, "altura_total_m": P['h']},
           "acceso_mantenimiento_previsto": True,
           "resistividad_ohm_cm": 500, "abrasion": "severamente_abrasivo"}}, open(f"{out}/externos.json", 'w'), indent=1)
json.dump({"corredor_del_proyecto": {"valor": "VALIDACION TDOT Ej. 4 (DATOS DE PRUEBA)",
           "trazabilidad": "DATOS DE PRUEBA, NO DEL PROYECTO: rotulo del caso de validacion externa (TDOT cap. 6 Ej. 4)", "fecha": "2026-11-15"}},
          open(f"{out}/sitio.json", 'w'), indent=1)
