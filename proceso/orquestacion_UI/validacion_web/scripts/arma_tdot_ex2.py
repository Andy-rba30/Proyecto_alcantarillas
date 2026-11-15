"""Arma las entradas de la app para TDOT Ejemplo 2 (HY-8), 10 caudales.
Cada caudal es un punto del CSV. Datos PUBLICADOS: Q, cotas de invert
(341.25 / 340.70 ft), L = 110 ft, S = 0.005, D = 36 in, n = 0.013 (concreto),
entrada square edge with headwall, cauce trapezoidal b = 3 ft, z = 3:1,
S = 0.005, n = 0.065, fondo 340.70 ft; calzada 345.32 ft; coronacion 30 ft.
DATOS DE PRUEBA (no publicados, rotulados): area_ha, cota_terreno,
cota_subrasante, cbr_subrasante, esviaje, sucs_fundacion, luz_m,
altura_total_m del cauce, progresivas."""
import json, sys, csv
sys.path.insert(0, '/tmp/validacion_web/scripts')
from conv import ft, cfs
out = sys.argv[1]
variante = sys.argv[2] if len(sys.argv) > 2 else 'base'
# --- datos de prueba (variante 'alt' los mueve para demostrar invariancia)
P = dict(base=dict(area_ha=50.0, terreno_sobre_invert_m=0.0, paquete_m=0.15,
                   cbr=10.0, sucs='SM', luz=3.0, h_cauce=3.0, rasante_extra_m=1.25),
         alt=dict(area_ha=500.0, terreno_sobre_invert_m=0.30, paquete_m=0.30,
                  cbr=4.0, sucs='GW', luz=5.0, h_cauce=6.0, rasante_extra_m=2.25),
         publicada=dict(area_ha=50.0, terreno_sobre_invert_m=0.0, paquete_m=0.15,
                   cbr=10.0, sucs='SM', luz=3.0, h_cauce=3.0, rasante_extra_m=0.0))[variante]
# rasante: la PUBLICADA es la del hombro, 345.32 ft. Con ella la app rechaza el 36 in
# por V4 (resguardo MTC por CBR) y V7 (flotacion): variante 'publicada'. Para leer
# la hidraulica del 36 in se sube la rasante como DATO DE PRUEBA (rasante_extra_m).
inv_ent = ft(341.25); inv_sal = ft(340.70); rasante = ft(345.32) + P['rasante_extra_m']
cols = "id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,cota_coronacion_canal".split(',')
filas = []
for i, q in enumerate([2.5*k for k in range(1, 11)]):
    Q = cfs(q)
    filas.append(dict(id=f"Q{q:04.1f}cfs".replace('.', 'p'), progresiva_km=f"{i}+{(i*100)%1000:03d}" if False else f"0+{100*(i+1):03d}" if i < 9 else "1+000",
        familia='A', Q_m3s=f"{Q:.6f}", area_ha=f"{P['area_ha']}", S_cauce="0.005",
        cota_terreno=f"{inv_ent + P['terreno_sobre_invert_m']:.6f}", cota_rasante=f"{rasante:.6f}",
        cota_subrasante=f"{rasante - P['paquete_m']:.6f}", cbr_subrasante=f"{P['cbr']}",
        esviaje_grados="0", ancho_plataforma=f"{ft(30.0):.6f}", cota_fondo_receptor=f"{inv_sal:.6f}",
        Q_receptor_m3s=f"{Q:.6f}", cota_TW="", sucs_fundacion=P['sucs'], NF_profundidad_m="",
        cota_fondo_entrada=f"{inv_ent:.6f}", cota_coronacion_canal=""))
with open(f"{out}/puntos.csv", 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(filas)
ext = {"globales": {"luz_m": P['luz'], "longitud_m": ft(110.0), "S_conducto": 0.005,
       "seccion_receptor_medida": {"b_m": ft(3.0), "z_HV": 3.0, "S": 0.005, "n": 0.065,
                                   "altura_total_m": P['h_cauce']},
       "acceso_mantenimiento_previsto": True}}
json.dump(ext, open(f"{out}/externos.json", 'w'), indent=1)
sitio = {"corredor_del_proyecto": {"valor": "VALIDACION TDOT Ej. 2 (DATOS DE PRUEBA)",
         "trazabilidad": "DATOS DE PRUEBA, NO DEL PROYECTO: rotulo del caso de validacion externa (TDOT Drainage Manual cap. 6 Ej. 2)",
         "fecha": "2026-11-15"}}
json.dump(sitio, open(f"{out}/sitio.json", 'w'), indent=1)
print(open(f"{out}/puntos.csv").read())
